/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright © 2013-2017 Red Hat, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>
#include <xorg-server.h>
#include <list.h>
#include <exevents.h>
#include <xkbsrv.h>
#include <xf86.h>
#include <xf86Xinput.h>
#include <xf86_OSproc.h>
#include <xserver-properties.h>
#include <libinput.h>
#include <linux/input.h>

#include <X11/Xatom.h>

#include "bezier.h"
#include "draglock.h"
#include "libinput-properties.h"

#define TOUCHPAD_NUM_AXES 4 /* x, y, hscroll, vscroll */
#define TABLET_NUM_BUTTONS 7 /* we need scroll buttons */
#define TOUCH_MAX_SLOTS 15
#define XORG_KEYCODE_OFFSET 8
#define SCROLL_INCREMENT 15
#define TOUCHPAD_SCROLL_DIST_MIN 10 /* in libinput pixels */
#define TOUCHPAD_SCROLL_DIST_MAX 50 /* in libinput pixels */

#define streq(a, b) (strcmp(a, b) == 0)
#define strneq(a, b, n) (strncmp(a, b, n) == 0)

/*
   libinput does not provide axis information for absolute devices, instead
   it scales into the screen dimensions provided. So we set up the axes with
   a fixed range, let libinput scale into that range and then the server
   do the scaling it usually does.
 */
#define TOUCH_AXIS_MAX 0xffff
#define TABLET_AXIS_MAX 0xffffff
#define TABLET_PRESSURE_AXIS_MAX 2047
#define TABLET_TILT_AXIS_MAX 64
#define TABLET_STRIP_AXIS_MAX 4096
#define TABLET_RING_AXIS_MAX 71

#define CAP_KEYBOARD	0x1
#define CAP_POINTER	0x2
#define CAP_TOUCH	0x4
#define CAP_TABLET	0x8
#define CAP_TABLET_TOOL	0x10
#define CAP_TABLET_PAD	0x20

struct xf86libinput_driver {
	struct libinput *libinput;
	int device_enabled_count;
	void *registered_InputInfoPtr;
};

static struct xf86libinput_driver driver_context;

struct xf86libinput_device {
	int refcount;
	int enabled_count;
	uint32_t id;
	struct libinput_device *device;
	struct xorg_list device_list;
	int server_fd;

	struct xorg_list unclaimed_tablet_tool_list;
};

struct xf86libinput_tablet_tool_queued_event {
	struct xorg_list node;
	struct libinput_event_tablet_tool *event;
};

struct xf86libinput_tablet_tool_event_queue {
	bool need_to_queue;
	struct xorg_list event_list;
};

struct xf86libinput_tablet_tool {
	struct xorg_list node;
	struct libinput_tablet_tool *tool;
};

struct xf86libinput {
	InputInfoPtr pInfo;
	char *path;
	uint32_t capabilities;

	struct {
		struct scroll_axis {
			int dist;
			double fraction;
		} v, h;
	} scroll;

	struct {
		double x;
		double y;
		double x_remainder;
		double y_remainder;
	} scale;

	BOOL has_abs;

	ValuatorMask *valuators;
	ValuatorMask *valuators_unaccelerated;

	struct options {
		BOOL tapping;
		BOOL tap_drag;
		BOOL tap_drag_lock;
		enum libinput_config_tap_button_map tap_button_map;
		BOOL natural_scrolling;
		BOOL left_handed;
		BOOL middle_emulation;
		BOOL disable_while_typing;
		CARD32 sendevents;
		CARD32 scroll_button; /* xorg button number */
		BOOL scroll_buttonlock;
		uint32_t scroll_pixel_distance;
		float speed;
		float matrix[9];
		enum libinput_config_scroll_method scroll_method;
		enum libinput_config_click_method click_method;
		enum libinput_config_accel_profile accel_profile;

		unsigned char btnmap[MAX_BUTTONS + 1];

		BOOL horiz_scrolling_enabled;

		float rotation_angle;
		struct bezier_control_point pressurecurve[4];
		struct ratio {
			int x, y;
		} area;
	} options;

	struct draglock draglock;

	struct xf86libinput_device *shared_device;
	struct xorg_list shared_device_link;

	struct libinput_tablet_tool *tablet_tool;

	bool allow_mode_group_updates;

	/* Pre-calculated pressure curve.
	   In the 0...TABLET_AXIS_MAX range */
	struct {
		int *values;
		size_t sz;
	} pressurecurve;

	struct scale_factor {
		double x, y;
	} area_scale_factor;
};

enum event_handling {
	EVENT_QUEUED,
	EVENT_HANDLED,
};

static void
xf86libinput_create_subdevice(InputInfoPtr pInfo,
			      uint32_t capabilities,
			      XF86OptionPtr extra_opts);
static inline void
update_mode_prop(InputInfoPtr pInfo,
		 struct libinput_event_tablet_pad *event);

static enum event_handling
xf86libinput_handle_event(struct libinput_event *event);

static void
xf86libinput_post_tablet_motion(InputInfoPtr pInfo,
				struct libinput_event_tablet_tool *event);

static inline int
use_server_fd(const InputInfoPtr pInfo) {
	return pInfo->fd > -1 && (pInfo->flags & XI86_SERVER_FD);
}

static inline unsigned int
btn_linux2xorg(unsigned int b)
{
	unsigned int button;

	switch(b) {
	case 0: button = 0; break;
	case BTN_LEFT: button = 1; break;
	case BTN_MIDDLE: button = 2; break;
	case BTN_RIGHT: button = 3; break;
	/* tablet button range */
	case BTN_STYLUS: button = 2; break;
	case BTN_STYLUS2: button = 3; break;
	default:
		button = 8 + b - BTN_SIDE;
		break;
	}

	return button;
}
static inline unsigned int
btn_xorg2linux(unsigned int b)
{
	unsigned int button;

	switch(b) {
	case 0: button = 0; break;
	case 1: button = BTN_LEFT; break;
	case 2: button = BTN_MIDDLE; break;
	case 3: button = BTN_RIGHT; break;
	default:
		button = b - 8 + BTN_SIDE;
		break;
	}

	return button;
}

static BOOL
xf86libinput_is_subdevice(InputInfoPtr pInfo)
{
	char *source;
	BOOL is_subdevice;

	source = xf86SetStrOption(pInfo->options, "_source", "");
	is_subdevice = streq(source, "_driver/libinput");
	free(source);

	return is_subdevice;
}

static inline InputInfoPtr
xf86libinput_get_parent(InputInfoPtr pInfo)
{
	InputInfoPtr parent;
	int parent_id;

	parent_id = xf86CheckIntOption(pInfo->options, "_libinput/shared-device", -1);
	if (parent_id == -1)
		return NULL;

	nt_list_for_each_entry(parent, xf86FirstLocalDevice(), next) {
		int id = xf86CheckIntOption(parent->options,
					    "_libinput/shared-device",
					    -1);
		if (id == parent_id && !xf86libinput_is_subdevice(parent))
			return parent;
	}

	return NULL;
}

static inline struct xf86libinput_device*
xf86libinput_shared_create(struct libinput_device *device)
{
	static uint32_t next_shared_device_id;
	struct xf86libinput_device *shared_device;

	shared_device = calloc(1, sizeof(*shared_device));
	if (!shared_device)
		return NULL;

	shared_device->device = device;
	shared_device->refcount = 1;
	shared_device->id = ++next_shared_device_id;
	xorg_list_init(&shared_device->device_list);
	xorg_list_init(&shared_device->unclaimed_tablet_tool_list);

	return shared_device;
}

static inline struct xf86libinput_device*
xf86libinput_shared_ref(struct xf86libinput_device *shared_device)
{
	shared_device->refcount++;

	return shared_device;
}

static inline struct xf86libinput_device*
xf86libinput_shared_unref(struct xf86libinput_device *shared_device)
{
	shared_device->refcount--;

	if (shared_device->refcount > 0)
		return shared_device;

	free(shared_device);

	return NULL;
}

static inline struct libinput_device *
xf86libinput_shared_enable(InputInfoPtr pInfo,
			   struct xf86libinput_device *shared_device,
			   const char *path)
{
	struct libinput_device *device;
	struct libinput *libinput = driver_context.libinput;

	/* With systemd-logind the server requests the fd from logind, sets
	 * pInfo->fd and sets the "fd" option to the fd number.
	 *
	 * If we have a second device that uses the same path, the server
	 * checks all pInfo->major/minor for a match and returns the matched
	 * device's pInfo->fd. In this driver, this fd is the epollfd, not
	 * the actual device. This causes troubles when removing the
	 * device.
	 *
	 * What we need to do here is: after enabling the device the first
	 * time extract the real fd and store it in the shared device
	 * struct. The second device replaces the pInfo->options "fd" with
	 * the real fd we're using.
	 *
	 * When the device is unplugged, the server now correctly finds two
	 * devices on the real fd and releases them in order.
	 */
	shared_device->enabled_count++;
	if (shared_device->enabled_count > 1) {
		if (pInfo->flags & XI86_SERVER_FD) {
			pInfo->options = xf86ReplaceIntOption(pInfo->options,
							      "fd",
							      shared_device->server_fd);
		}

		return shared_device->device;
	}

	device = libinput_path_add_device(libinput, path);
	if (!device)
		return NULL;

	libinput_device_set_user_data(device, shared_device);
	shared_device->device = libinput_device_ref(device);

	if (pInfo->flags & XI86_SERVER_FD)
		shared_device->server_fd = xf86CheckIntOption(pInfo->options,
							      "fd",
							      -1);
	return device;
}

static inline void
xf86libinput_shared_disable(struct xf86libinput_device *shared_device)
{
	struct libinput_device *device = shared_device->device;

	shared_device->enabled_count--;

	if (shared_device->enabled_count > 0)
		return;

	if (!device)
		return;

	libinput_device_set_user_data(device, NULL);
	libinput_path_remove_device(device);
	libinput_device_unref(device);
	shared_device->device = NULL;
}

static inline bool
xf86libinput_shared_is_enabled(struct xf86libinput_device *shared_device)
{
	return shared_device->enabled_count > 0;
}

static inline bool
xf86libinput_set_pressurecurve(struct xf86libinput *driver_data,
			       const struct bezier_control_point controls[4])
{
	if (memcmp(controls, bezier_defaults, sizeof(bezier_defaults)) == 0) {
		free(driver_data->pressurecurve.values);
		driver_data->pressurecurve.values = NULL;
		return true;
	}

	if (!driver_data->pressurecurve.values) {
		int *vals = calloc(TABLET_PRESSURE_AXIS_MAX + 1, sizeof(int));
		if (!vals)
			return false;

		driver_data->pressurecurve.values = vals;
		driver_data->pressurecurve.sz = TABLET_PRESSURE_AXIS_MAX + 1;
	}

	return cubic_bezier(controls,
			    driver_data->pressurecurve.values,
			    driver_data->pressurecurve.sz);
}

static inline void
xf86libinput_set_area_ratio(struct xf86libinput *driver_data,
			    const struct ratio *ratio)
{
	double f;
	double w, h;

	if (libinput_device_get_size(driver_data->shared_device->device, &w, &h) != 0)
		return;

	driver_data->options.area = *ratio;

	if (ratio->y == 0) {
		driver_data->area_scale_factor.x = 1.0;
		driver_data->area_scale_factor.y = 1.0;
		return;
	}

	f = 1.0 * (ratio->x * h)/(ratio->y * w);

	if (f <= 1.0) {
		driver_data->area_scale_factor.x = 1.0/f;
		driver_data->area_scale_factor.y = 1.0;
	} else {
		driver_data->area_scale_factor.x = 1.0;
		driver_data->area_scale_factor.y = f;
	}
}

/**
 * returns true if the device has one or more of the given capabilities or
 * if the device isn't a subdevice
 */
static inline bool
subdevice_has_capabilities(DeviceIntPtr dev, uint32_t capabilities)
{
	InputInfoPtr pInfo  = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;

	if (!xf86libinput_is_subdevice(pInfo))
		return true;

	return !!(driver_data->capabilities & capabilities);
}

static int
LibinputSetProperty(DeviceIntPtr dev, Atom atom, XIPropertyValuePtr val,
                 BOOL checkonly);
static void
LibinputInitProperty(DeviceIntPtr dev);

static void
LibinputApplyConfigSendEvents(DeviceIntPtr dev,
			      struct xf86libinput *driver_data,
			      struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (libinput_device_config_send_events_get_modes(device) != LIBINPUT_CONFIG_SEND_EVENTS_ENABLED &&
	    libinput_device_config_send_events_set_mode(device,
							driver_data->options.sendevents) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set SendEventsMode %u\n",
			    driver_data->options.sendevents);
}

static void
LibinputApplyConfigNaturalScroll(DeviceIntPtr dev,
				 struct xf86libinput *driver_data,
				 struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_scroll_has_natural_scroll(device) &&
	    libinput_device_config_scroll_set_natural_scroll_enabled(device,
								     driver_data->options.natural_scrolling) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set NaturalScrolling to %d\n",
			    driver_data->options.natural_scrolling);
}

static void
LibinputApplyConfigAccel(DeviceIntPtr dev,
			 struct xf86libinput *driver_data,
			 struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_accel_is_available(device) &&
	    libinput_device_config_accel_set_speed(device,
						   driver_data->options.speed) != LIBINPUT_CONFIG_STATUS_SUCCESS)
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Failed to set speed %.2f\n",
				    driver_data->options.speed);

	if (libinput_device_config_accel_get_profiles(device) &&
	    driver_data->options.accel_profile != LIBINPUT_CONFIG_ACCEL_PROFILE_NONE  &&
	    libinput_device_config_accel_set_profile(device,
						     driver_data->options.accel_profile) !=
			    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		const char *profile;

		switch (driver_data->options.accel_profile) {
		case LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE:
			profile = "adaptive";
			break;
		case LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT:
			profile = "flat";
			break;
		default:
			profile = "unknown";
			break;
		}
		xf86IDrvMsg(pInfo, X_ERROR, "Failed to set profile %s\n", profile);
	}
}

static inline void
LibinputApplyConfigTap(DeviceIntPtr dev,
		       struct xf86libinput *driver_data,
		       struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_tap_get_finger_count(device) > 0 &&
	    libinput_device_config_tap_set_enabled(device,
						   driver_data->options.tapping) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping to %d\n",
			    driver_data->options.tapping);

	if (libinput_device_config_tap_get_finger_count(device) > 0 &&
	    libinput_device_config_tap_set_button_map(device,
						      driver_data->options.tap_button_map) != LIBINPUT_CONFIG_STATUS_SUCCESS) {
		const char *map;

		switch(driver_data->options.tap_button_map) {
		case LIBINPUT_CONFIG_TAP_MAP_LRM: map = "lrm"; break;
		case LIBINPUT_CONFIG_TAP_MAP_LMR: map = "lmr"; break;
		default: map = "unknown"; break;
		}
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping ButtonMap to %s\n",
			    map);
	}

	if (libinput_device_config_tap_get_finger_count(device) > 0 &&
	    libinput_device_config_tap_set_drag_lock_enabled(device,
							     driver_data->options.tap_drag_lock) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping DragLock to %d\n",
			    driver_data->options.tap_drag_lock);

	if (libinput_device_config_tap_get_finger_count(device) > 0 &&
	    libinput_device_config_tap_set_drag_enabled(device,
							driver_data->options.tap_drag) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping Drag to %d\n",
			    driver_data->options.tap_drag);
}

static void
LibinputApplyConfigCalibration(DeviceIntPtr dev,
			       struct xf86libinput *driver_data,
			       struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_TOUCH|CAP_TABLET))
		return;

	if (libinput_device_config_calibration_has_matrix(device) &&
	    libinput_device_config_calibration_set_matrix(device,
							  driver_data->options.matrix) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to apply matrix: "
			    "%.2f %.2f %.2f %2.f %.2f %.2f %.2f %.2f %.2f\n",
			    driver_data->options.matrix[0], driver_data->options.matrix[1],
			    driver_data->options.matrix[2], driver_data->options.matrix[3],
			    driver_data->options.matrix[4], driver_data->options.matrix[5],
			    driver_data->options.matrix[6], driver_data->options.matrix[7],
			    driver_data->options.matrix[8]);
}

static void
LibinputApplyConfigLeftHanded(DeviceIntPtr dev,
			       struct xf86libinput *driver_data,
			       struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER|CAP_TABLET))
		return;

	if (libinput_device_config_left_handed_is_available(device) &&
	    libinput_device_config_left_handed_set(device,
						   driver_data->options.left_handed) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set LeftHanded to %d\n",
			    driver_data->options.left_handed);
}

static void
LibinputApplyConfigScrollMethod(DeviceIntPtr dev,
				struct xf86libinput *driver_data,
				struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_scroll_set_method(device,
						     driver_data->options.scroll_method) != LIBINPUT_CONFIG_STATUS_SUCCESS) {
		const char *method;

		switch(driver_data->options.scroll_method) {
		case LIBINPUT_CONFIG_SCROLL_NO_SCROLL: method = "none"; break;
		case LIBINPUT_CONFIG_SCROLL_2FG: method = "twofinger"; break;
		case LIBINPUT_CONFIG_SCROLL_EDGE: method = "edge"; break;
		case LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN: method = "button"; break;
		default:
			method = "unknown"; break;
		}

		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set scroll to %s\n",
			    method);
	}

	if (libinput_device_config_scroll_get_methods(device) & LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN) {
		unsigned int scroll_button;
#if HAVE_LIBINPUT_SCROLL_BUTTON_LOCK
		enum libinput_config_scroll_button_lock_state buttonlock;

		buttonlock = driver_data->options.scroll_buttonlock ?
				LIBINPUT_CONFIG_SCROLL_BUTTON_LOCK_ENABLED :
				LIBINPUT_CONFIG_SCROLL_BUTTON_LOCK_DISABLED;

		if (libinput_device_config_scroll_set_button_lock(device, buttonlock)
		    != LIBINPUT_CONFIG_STATUS_SUCCESS) {
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Failed to %s ScrollButtonLock\n",
				    buttonlock ? "enable" : "disable");
		}
#endif

		scroll_button = btn_xorg2linux(driver_data->options.scroll_button);
		if (libinput_device_config_scroll_set_button(device, scroll_button) != LIBINPUT_CONFIG_STATUS_SUCCESS)
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Failed to set ScrollButton to %u\n",
				    driver_data->options.scroll_button);

	}
}

static void
LibinputApplyConfigClickMethod(DeviceIntPtr dev,
			       struct xf86libinput *driver_data,
			       struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_click_set_method(device,
						    driver_data->options.click_method) != LIBINPUT_CONFIG_STATUS_SUCCESS) {
		const char *method;

		switch (driver_data->options.click_method) {
		case LIBINPUT_CONFIG_CLICK_METHOD_NONE: method = "none"; break;
		case LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS: method = "buttonareas"; break;
		case LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER: method = "clickfinger"; break;
		default:
			method = "unknown"; break;
		}

		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set click method to %s\n",
			    method);
	}
}

static void
LibinputApplyConfigMiddleEmulation(DeviceIntPtr dev,
				   struct xf86libinput *driver_data,
				   struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_middle_emulation_is_available(device) &&
	    libinput_device_config_middle_emulation_set_enabled(device,
								driver_data->options.middle_emulation) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set MiddleEmulation to %d\n",
			    driver_data->options.middle_emulation);
}

static void
LibinputApplyConfigDisableWhileTyping(DeviceIntPtr dev,
				      struct xf86libinput *driver_data,
				      struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_dwt_is_available(device) &&
	    libinput_device_config_dwt_set_enabled(device,
						   driver_data->options.disable_while_typing) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set DisableWhileTyping to %d\n",
			    driver_data->options.disable_while_typing);
}

static void
LibinputApplyConfigRotation(DeviceIntPtr dev,
			    struct xf86libinput *driver_data,
			    struct libinput_device *device)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_rotation_is_available(device) &&
	    libinput_device_config_rotation_set_angle(device, driver_data->options.rotation_angle) != LIBINPUT_CONFIG_STATUS_SUCCESS)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set RotationAngle to %.2f\n",
			    driver_data->options.rotation_angle);
}

static inline void
LibinputApplyConfig(DeviceIntPtr dev)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;

	LibinputApplyConfigSendEvents(dev, driver_data, device);
	LibinputApplyConfigNaturalScroll(dev, driver_data, device);
	LibinputApplyConfigAccel(dev, driver_data, device);
	LibinputApplyConfigTap(dev, driver_data, device);
	LibinputApplyConfigCalibration(dev, driver_data, device);
	LibinputApplyConfigLeftHanded(dev, driver_data, device);
	LibinputApplyConfigScrollMethod(dev, driver_data, device);
	LibinputApplyConfigClickMethod(dev, driver_data, device);
	LibinputApplyConfigMiddleEmulation(dev, driver_data, device);
	LibinputApplyConfigDisableWhileTyping(dev, driver_data, device);
	LibinputApplyConfigRotation(dev, driver_data, device);
}

static int
xf86libinput_on(DeviceIntPtr dev)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;
	struct libinput *libinput = driver_context.libinput;
	struct libinput_device *device;

	device = xf86libinput_shared_enable(pInfo,
					    shared_device,
					    driver_data->path);
	if (!device)
		return !Success;

	/* if we use server fds, overwrite the fd with the one from
	   libinput nonetheless, otherwise the server won't call ReadInput
	   for our device. This must be swapped back to the real fd in
	   DEVICE_OFF so systemd-logind closes the right fd */
	pInfo->fd = libinput_get_fd(libinput);

	if (driver_context.device_enabled_count == 0) {
		xf86AddEnabledDevice(pInfo);
		driver_context.registered_InputInfoPtr = pInfo;
	}

	driver_context.device_enabled_count++;
	dev->public.on = TRUE;

	LibinputApplyConfig(dev);

	return Success;
}

static int
xf86libinput_off(DeviceIntPtr dev)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;

	if (--driver_context.device_enabled_count == 0) {
		xf86RemoveEnabledDevice(pInfo);
	}

	if (use_server_fd(pInfo)) {
		pInfo->fd = xf86SetIntOption(pInfo->options, "fd", -1);
	} else {
		pInfo->fd = -1;
	}

	dev->public.on = FALSE;

	xf86libinput_shared_disable(shared_device);

	return Success;
}

static void
xf86libinput_ptr_ctl(DeviceIntPtr dev, PtrCtrl *ctl)
{
}

static void
init_button_map(unsigned char *btnmap, size_t size)
{
	int i;

	memset(btnmap, 0, size);
	for (i = 0; i < size; i++)
		btnmap[i] = i;
}

static void
init_button_labels(Atom *labels, size_t size)
{
	assert(size > 10);

	memset(labels, 0, size * sizeof(Atom));
	labels[0] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_LEFT);
	labels[1] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_MIDDLE);
	labels[2] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_RIGHT);
	labels[3] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_WHEEL_UP);
	labels[4] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_WHEEL_DOWN);
	labels[5] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_HWHEEL_LEFT);
	labels[6] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_HWHEEL_RIGHT);
	labels[7] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_SIDE);
	labels[8] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_EXTRA);
	labels[9] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_FORWARD);
	labels[10] = XIGetKnownProperty(BTN_LABEL_PROP_BTN_BACK);
}

static void
init_axis_labels(Atom *labels, size_t size)
{
	memset(labels, 0, size * sizeof(Atom));
	labels[0] = XIGetKnownProperty(AXIS_LABEL_PROP_REL_X);
	labels[1] = XIGetKnownProperty(AXIS_LABEL_PROP_REL_Y);
	labels[2] = XIGetKnownProperty(AXIS_LABEL_PROP_REL_HSCROLL);
	labels[3] = XIGetKnownProperty(AXIS_LABEL_PROP_REL_VSCROLL);
}

static int
xf86libinput_init_pointer(InputInfoPtr pInfo)
{
	DeviceIntPtr dev= pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	int min, max, res;
	int nbuttons = 7;
	int i;

	Atom btnlabels[MAX_BUTTONS];
	Atom axislabels[TOUCHPAD_NUM_AXES];

	for (i = BTN_JOYSTICK - 1; i >= BTN_SIDE; i--) {
		if (libinput_device_pointer_has_button(device, i)) {
			nbuttons += i - BTN_SIDE + 1;
			break;
		}
	}

	init_button_labels(btnlabels, ARRAY_SIZE(btnlabels));
	init_axis_labels(axislabels, ARRAY_SIZE(axislabels));

	InitPointerDeviceStruct((DevicePtr)dev,
				driver_data->options.btnmap,
				nbuttons,
				btnlabels,
				xf86libinput_ptr_ctl,
				GetMotionHistorySize(),
				TOUCHPAD_NUM_AXES,
				axislabels);
	min = -1;
	max = -1;
	res = 0;

	xf86InitValuatorAxisStruct(dev, 0,
			           XIGetKnownProperty(AXIS_LABEL_PROP_REL_X),
				   min, max, res * 1000, 0, res * 1000, Relative);
	xf86InitValuatorAxisStruct(dev, 1,
			           XIGetKnownProperty(AXIS_LABEL_PROP_REL_Y),
				   min, max, res * 1000, 0, res * 1000, Relative);

	SetScrollValuator(dev, 2, SCROLL_TYPE_HORIZONTAL, driver_data->scroll.h.dist, 0);
	SetScrollValuator(dev, 3, SCROLL_TYPE_VERTICAL, driver_data->scroll.v.dist, 0);

	return Success;
}

static int
xf86libinput_init_pointer_absolute(InputInfoPtr pInfo)
{
	DeviceIntPtr dev= pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	int min, max, res;
	int nbuttons = 7;
	int i;

	Atom btnlabels[MAX_BUTTONS];
	Atom axislabels[TOUCHPAD_NUM_AXES];

	for (i = BTN_BACK; i >= BTN_SIDE; i--) {
		if (libinput_device_pointer_has_button(device, i)) {
			nbuttons += i - BTN_SIDE + 1;
			break;
		}
	}

	init_button_labels(btnlabels, ARRAY_SIZE(btnlabels));
	init_axis_labels(axislabels, ARRAY_SIZE(axislabels));

	InitPointerDeviceStruct((DevicePtr)dev,
				driver_data->options.btnmap,
				nbuttons,
				btnlabels,
				xf86libinput_ptr_ctl,
				GetMotionHistorySize(),
				TOUCHPAD_NUM_AXES,
				axislabels);
	min = 0;
	max = TOUCH_AXIS_MAX;
	res = 0;

	xf86InitValuatorAxisStruct(dev, 0,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_X),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	xf86InitValuatorAxisStruct(dev, 1,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_Y),
				   min, max, res * 1000, 0, res * 1000, Absolute);

	SetScrollValuator(dev, 2, SCROLL_TYPE_HORIZONTAL, driver_data->scroll.h.dist, 0);
	SetScrollValuator(dev, 3, SCROLL_TYPE_VERTICAL, driver_data->scroll.v.dist, 0);

	driver_data->has_abs = TRUE;

	return Success;
}
static void
xf86libinput_kbd_ctrl(DeviceIntPtr device, KeybdCtrl *ctrl)
{
#define CAPSFLAG	1
#define NUMFLAG		2
#define SCROLLFLAG	4

    static struct { int xbit, code; } bits[] = {
        { CAPSFLAG,	LIBINPUT_LED_CAPS_LOCK },
        { NUMFLAG,	LIBINPUT_LED_NUM_LOCK },
        { SCROLLFLAG,	LIBINPUT_LED_SCROLL_LOCK },
	{ 0, 0 },
    };
    int i = 0;
    enum libinput_led leds = 0;
    InputInfoPtr pInfo = device->public.devicePrivate;
    struct xf86libinput *driver_data = pInfo->private;
    struct libinput_device *ldevice = driver_data->shared_device->device;

    if (!device->enabled)
	    return;

    while (bits[i].xbit) {
	    if (ctrl->leds & bits[i].xbit)
		    leds |= bits[i].code;
	    i++;
    }

    libinput_device_led_update(ldevice, leds);
}

static void
xf86libinput_init_keyboard(InputInfoPtr pInfo)
{
	DeviceIntPtr dev= pInfo->dev;
	XkbRMLVOSet rmlvo = {0};
	XkbRMLVOSet defaults = {0};

	XkbGetRulesDflts(&defaults);

	rmlvo.rules = xf86SetStrOption(pInfo->options,
				       "xkb_rules",
				       defaults.rules);
	rmlvo.model = xf86SetStrOption(pInfo->options,
				       "xkb_model",
				       defaults.model);
	rmlvo.layout = xf86SetStrOption(pInfo->options,
					"xkb_layout",
					defaults.layout);
	rmlvo.variant = xf86SetStrOption(pInfo->options,
					 "xkb_variant",
					 defaults.variant);
	rmlvo.options = xf86SetStrOption(pInfo->options,
					 "xkb_options",
					 defaults.options);

	InitKeyboardDeviceStruct(dev, &rmlvo, NULL,
				 xf86libinput_kbd_ctrl);
	XkbFreeRMLVOSet(&rmlvo, FALSE);
	XkbFreeRMLVOSet(&defaults, FALSE);
}

static void
xf86libinput_init_touch(InputInfoPtr pInfo)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	int min, max, res;
	Atom btnlabels[MAX_BUTTONS];
	Atom axislabels[TOUCHPAD_NUM_AXES];
	int nbuttons = 7;
	int ntouches = TOUCH_MAX_SLOTS;

	init_button_labels(btnlabels, ARRAY_SIZE(btnlabels));
	init_axis_labels(axislabels, ARRAY_SIZE(axislabels));

	InitPointerDeviceStruct((DevicePtr)dev,
				driver_data->options.btnmap,
				nbuttons,
				btnlabels,
				xf86libinput_ptr_ctl,
				GetMotionHistorySize(),
				TOUCHPAD_NUM_AXES,
				axislabels);
	min = 0;
	max = TOUCH_AXIS_MAX;
	res = 0;

	xf86InitValuatorAxisStruct(dev, 0,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_MT_POSITION_X),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	xf86InitValuatorAxisStruct(dev, 1,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_MT_POSITION_Y),
				   min, max, res * 1000, 0, res * 1000, Absolute);

	ntouches = libinput_device_touch_get_touch_count(device);
	if (ntouches == 0) /* unknown -  mtdev */
		ntouches = TOUCH_MAX_SLOTS;
	InitTouchClassDeviceStruct(dev, ntouches, XIDirectTouch, 2);

}

static int
xf86libinput_init_tablet_pen_or_eraser(InputInfoPtr pInfo,
				       struct libinput_tablet_tool *tool)
{
	DeviceIntPtr dev = pInfo->dev;
	int min, max, res;
	int axis;

	min = 0;
	max = TABLET_PRESSURE_AXIS_MAX;
	res = 0;
	axis = 2;
	if (libinput_tablet_tool_has_pressure(tool))
		xf86InitValuatorAxisStruct(dev, axis++,
					   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_PRESSURE),
					   min, max, res * 1000, 0, res * 1000, Absolute);
	max = TABLET_TILT_AXIS_MAX;
	min = -TABLET_TILT_AXIS_MAX;
	if (libinput_tablet_tool_has_tilt(tool)) {
		xf86InitValuatorAxisStruct(dev, axis++,
					   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_TILT_X),
					   min, max, res * 1000, 0, res * 1000, Absolute);
		xf86InitValuatorAxisStruct(dev, axis++,
					   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_TILT_Y),
					   min, max, res * 1000, 0, res * 1000, Absolute);
	}

	min = -TABLET_AXIS_MAX;
	max = TABLET_AXIS_MAX;
	if (libinput_tablet_tool_has_rotation(tool))
		xf86InitValuatorAxisStruct(dev, axis++,
					   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_RZ),
					   min, max, res * 1000, 0, res * 1000, Absolute);
	return axis;
}

static void
xf86libinput_init_tablet_airbrush(InputInfoPtr pInfo,
				  struct libinput_tablet_tool *tool)
{
	DeviceIntPtr dev = pInfo->dev;
	int min, max, res;
	int axis;

	/* first axes are shared */
	axis = xf86libinput_init_tablet_pen_or_eraser(pInfo, tool);
	if (axis < 5) {
		xf86IDrvMsg(pInfo, X_ERROR, "Airbrush tool has missing pressure or tilt axes\n");
		return;
	}

	if (!libinput_tablet_tool_has_slider(tool)) {
		xf86IDrvMsg(pInfo, X_ERROR, "Airbrush tool is missing the slider axis\n");
		return;
	}

	min = -TABLET_AXIS_MAX;
	max = TABLET_AXIS_MAX;
	res = 0;

	xf86InitValuatorAxisStruct(dev, axis,
				   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_THROTTLE),
				   min, max, res * 1000, 0, res * 1000, Absolute);
}

static void
xf86libinput_init_tablet_mouse(InputInfoPtr pInfo,
			       struct libinput_tablet_tool *tool)
{
	DeviceIntPtr dev = pInfo->dev;
	int min, max, res;
	int axis;

	if (!libinput_tablet_tool_has_rotation(tool)) {
		xf86IDrvMsg(pInfo, X_ERROR, "Mouse tool is missing the rotation axis\n");
		return;
	}

	min = 0;
	max = TABLET_AXIS_MAX;
	res = 0;

	/* The mouse/lens tool don't have pressure, but for backwards-compat
	   with the xorg wacom driver we initialize the the axis anyway */
	axis = 2;
	xf86InitValuatorAxisStruct(dev, axis,
				   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_PRESSURE),
				   min, max, res * 1000, 0, res * 1000, Absolute);

	axis = 3;
	min = -TABLET_AXIS_MAX;
	max = TABLET_AXIS_MAX;
	xf86InitValuatorAxisStruct(dev, axis,
				   XIGetKnownProperty(AXIS_LABEL_PROP_ABS_RZ),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	return;
}

static void
xf86libinput_init_tablet(InputInfoPtr pInfo)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_tablet_tool *tool;
	int min, max, res;
	Atom btnlabels[TABLET_NUM_BUTTONS] = {0};
	Atom axislabels[TOUCHPAD_NUM_AXES] = {0};
	int nbuttons = TABLET_NUM_BUTTONS;
	int naxes = 2;

	BUG_RETURN(driver_data->tablet_tool == NULL);

	tool = driver_data->tablet_tool;

	if (libinput_tablet_tool_has_pressure(tool))
		naxes++;
	if (libinput_tablet_tool_has_tilt(tool))
		naxes += 2;
	if (libinput_tablet_tool_has_slider(tool))
		naxes++;
	if (libinput_tablet_tool_has_rotation(tool))
		naxes++;

	InitPointerDeviceStruct((DevicePtr)dev,
				driver_data->options.btnmap,
				nbuttons,
				btnlabels,
				xf86libinput_ptr_ctl,
				GetMotionHistorySize(),
				naxes,
				axislabels);

	min = 0;
	max = TABLET_AXIS_MAX;
	res = 0;
	xf86InitValuatorAxisStruct(dev, 0,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_X),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	xf86InitValuatorAxisStruct(dev, 1,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_Y),
				   min, max, res * 1000, 0, res * 1000, Absolute);

	switch (libinput_tablet_tool_get_type(tool)) {
	case LIBINPUT_TABLET_TOOL_TYPE_PEN:
	case LIBINPUT_TABLET_TOOL_TYPE_ERASER:
		xf86libinput_init_tablet_pen_or_eraser(pInfo, tool);
		break;
	case LIBINPUT_TABLET_TOOL_TYPE_AIRBRUSH:
		xf86libinput_init_tablet_airbrush(pInfo, tool);
		break;
	case LIBINPUT_TABLET_TOOL_TYPE_MOUSE:
	case LIBINPUT_TABLET_TOOL_TYPE_LENS:
		xf86libinput_init_tablet_mouse(pInfo, tool);
		break;
	default:
		xf86IDrvMsg(pInfo, X_ERROR, "Tool type not supported yet\n");
		break;
	}

	InitProximityClassDeviceStruct(dev);
}

static void
xf86libinput_init_tablet_pad(InputInfoPtr pInfo)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	int min, max, res;
	Atom btnlabels[MAX_BUTTONS] = {0};
	Atom axislabels[TOUCHPAD_NUM_AXES] = {0};
	int nbuttons;
	int naxes = 7;

	nbuttons = libinput_device_tablet_pad_get_num_buttons(device) + 4;

	InitPointerDeviceStruct((DevicePtr)dev,
				driver_data->options.btnmap,
				nbuttons,
				btnlabels,
				xf86libinput_ptr_ctl,
				GetMotionHistorySize(),
				naxes,
				axislabels);

	/* For compat with xf86-input-wacom we init x, y, pressure, followed
	 * by strip x, strip y, ring, ring2*/
	min = 0;
	max = TABLET_AXIS_MAX;
	res = 0;
	xf86InitValuatorAxisStruct(dev, 0,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_X),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	xf86InitValuatorAxisStruct(dev, 1,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_Y),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	xf86InitValuatorAxisStruct(dev, 2,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_PRESSURE),
				   min, max, res * 1000, 0, res * 1000, Absolute);

	/* strip x */
	max = TABLET_STRIP_AXIS_MAX;
	xf86InitValuatorAxisStruct(dev, 3,
			           None,
				   min, max, res * 1000, 0, res * 1000, Absolute);
	/* strip y */
	xf86InitValuatorAxisStruct(dev, 4,
			           None,
				   min, max, res * 1000, 0, res * 1000, Absolute);
	/* first ring */
	max = TABLET_RING_AXIS_MAX;
	xf86InitValuatorAxisStruct(dev, 5,
			           XIGetKnownProperty(AXIS_LABEL_PROP_ABS_WHEEL),
				   min, max, res * 1000, 0, res * 1000, Absolute);
	/* second ring */
	xf86InitValuatorAxisStruct(dev, 6,
			           None,
				   min, max, res * 1000, 0, res * 1000, Absolute);
}

static int
xf86libinput_init(DeviceIntPtr dev)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;
	struct libinput_device *device = shared_device->device;

	BUG_RETURN_VAL(device == NULL, !Success);

	dev->public.on = FALSE;

	if (driver_data->capabilities & CAP_KEYBOARD)
		xf86libinput_init_keyboard(pInfo);
	if (driver_data->capabilities & CAP_POINTER) {
		if (libinput_device_config_calibration_has_matrix(device) &&
		    !libinput_device_config_accel_is_available(device))
			xf86libinput_init_pointer_absolute(pInfo);
		else
			xf86libinput_init_pointer(pInfo);
	}
	if (driver_data->capabilities & CAP_TOUCH)
		xf86libinput_init_touch(pInfo);
	if (driver_data->capabilities & CAP_TABLET_TOOL)
		xf86libinput_init_tablet(pInfo);
	if (driver_data->capabilities & CAP_TABLET_PAD)
		xf86libinput_init_tablet_pad(pInfo);

	LibinputApplyConfig(dev);
	LibinputInitProperty(dev);
	XIRegisterPropertyHandler(dev, LibinputSetProperty, NULL, NULL);

	/* If we have a device but it's not yet enabled it's the
	 * already-removed device from PreInit. Drop the ref to clean up,
	 * we'll get a new libinput_device during DEVICE_ON when we re-add
	 * it. */
	if (!xf86libinput_shared_is_enabled(shared_device)) {
		libinput_device_unref(device);
		shared_device->device = NULL;
	}

	return 0;
}

static bool
is_libinput_device(InputInfoPtr pInfo)
{
	char *driver;
	BOOL rc;

	driver = xf86CheckStrOption(pInfo->options, "driver", "");
	rc = streq(driver, "libinput");
	free(driver);

	return rc;
}

static void
swap_registered_device(InputInfoPtr pInfo)
{
	InputInfoPtr next;

	if (pInfo != driver_context.registered_InputInfoPtr)
		return;

	next = xf86FirstLocalDevice();
	while (next == pInfo || !is_libinput_device(next))
		next = next->next;

	input_lock();
	xf86RemoveEnabledDevice(pInfo);
	xf86AddEnabledDevice(next);
	driver_context.registered_InputInfoPtr = next;
	input_unlock();
}

static void
xf86libinput_destroy(DeviceIntPtr dev)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;

	/* If the device being destroyed is the one we used for
	 * xf86AddEnabledDevice(), we need to swap it out for one that is
	 * still live. xf86AddEnabledDevice() buffers some data and once the
	 * deletes pInfo (when DEVICE_OFF completes) the thread will keep
	 * calling that struct's read_input because we never removed it.
	 * Avoid this by removing ours and substituting one that's still
	 * valid, the fd is the same anyway (libinput's epollfd).
	 */
	if (driver_context.device_enabled_count > 0)
		swap_registered_device(pInfo);

	xorg_list_del(&driver_data->shared_device_link);

	if (driver_data->tablet_tool)
		libinput_tablet_tool_unref(driver_data->tablet_tool);

	xf86libinput_shared_unref(shared_device);
}

static int
xf86libinput_device_control(DeviceIntPtr dev, int mode)
{
	int rc = BadValue;

	switch(mode) {
		case DEVICE_INIT:
			rc = xf86libinput_init(dev);
			break;
		case DEVICE_ON:
			rc = xf86libinput_on(dev);
			break;
		case DEVICE_OFF:
			rc = xf86libinput_off(dev);
			break;
		case DEVICE_CLOSE:
			xf86libinput_destroy(dev);
			rc = Success;
			break;
	}

	return rc;
}

static void
xf86libinput_handle_motion(InputInfoPtr pInfo, struct libinput_event_pointer *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	double x, y;

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	x = libinput_event_pointer_get_dx(event);
	y = libinput_event_pointer_get_dy(event);

	valuator_mask_zero(mask);

	{
		double ux, uy;

		ux = libinput_event_pointer_get_dx_unaccelerated(event);
		uy = libinput_event_pointer_get_dy_unaccelerated(event);

		valuator_mask_set_unaccelerated(mask, 0, x, ux);
		valuator_mask_set_unaccelerated(mask, 1, y, uy);
	}
	xf86PostMotionEventM(dev, Relative, mask);
}

static void
xf86libinput_handle_absmotion(InputInfoPtr pInfo, struct libinput_event_pointer *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	double x, y;

	if (!driver_data->has_abs) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Discarding absolute event from relative device. "
			    "Please file a bug\n");
		return;
	}

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	x = libinput_event_pointer_get_absolute_x_transformed(event, TOUCH_AXIS_MAX);
	y = libinput_event_pointer_get_absolute_y_transformed(event, TOUCH_AXIS_MAX);

	valuator_mask_zero(mask);
	valuator_mask_set_double(mask, 0, x);
	valuator_mask_set_double(mask, 1, y);

	xf86PostMotionEventM(dev, Absolute, mask);
}

static void
xf86libinput_handle_button(InputInfoPtr pInfo, struct libinput_event_pointer *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	int button;
	int is_press;

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	button = btn_linux2xorg(libinput_event_pointer_get_button(event));
	is_press = (libinput_event_pointer_get_button_state(event) == LIBINPUT_BUTTON_STATE_PRESSED);

	if (draglock_get_mode(&driver_data->draglock) != DRAGLOCK_DISABLED)
		draglock_filter_button(&driver_data->draglock, &button, &is_press);

	if (button && button < 256)
		xf86PostButtonEvent(dev, Relative, button, is_press, 0, 0);
}

static void
xf86libinput_handle_key(InputInfoPtr pInfo, struct libinput_event_keyboard *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	int is_press;
	int key = libinput_event_keyboard_get_key(event);

	if ((driver_data->capabilities & CAP_KEYBOARD) == 0)
		return;

	key += XORG_KEYCODE_OFFSET;

	is_press = (libinput_event_keyboard_get_key_state(event) == LIBINPUT_KEY_STATE_PRESSED);
	xf86PostKeyboardEvent(dev, key, is_press);
}

/*
 * The scroll fraction is the value we divide the scroll dist with to
 * accommodate for wheels with a small click angle. On these devices,
 * multiple clicks of small angle accumulate to the XI 2.1 scroll distance.
 * This gives us smooth scrolling on those wheels for small movements, the
 * legacy button events are generated whenever the full distance is reached.
 * e.g. a 2 degree click angle requires 8 clicks before a legacy event is
 * sent, but each of those clicks will send XI2.1 smooth scroll data for
 * compatible clients.
 *
 * Starting with kernel v5.0 we should get REL_WHEEL_HI_RES from those
 * devices for the fine-grained scrolling and REL_WHEEL for the normal one,
 * so the use-case above shouldn't matter anymore.
 */
static inline double
get_wheel_scroll_value(struct xf86libinput *driver_data,
		       struct libinput_event_pointer *event,
		       enum libinput_pointer_axis axis)
{
	struct scroll_axis *s;
	double f;
	double angle;
	int discrete;

	switch (axis) {
	case LIBINPUT_POINTER_AXIS_SCROLL_HORIZONTAL:
		s = &driver_data->scroll.h;
		break;
	case LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL:
		s = &driver_data->scroll.v;
		break;
	default:
		return 0.0;
	}

	angle = libinput_event_pointer_get_axis_value(event, axis);
	discrete = libinput_event_pointer_get_axis_value_discrete(event, axis);

	/* We only need to guess the fraction on the first set of
	 * scroll events until a discrete value arrives. Once known, we
	 * re-use the fraction until the device goes away.
	 */
	if (s->fraction != 0.0)
		goto out;

	/* if we get a discrete of 0, assume REL_WHEEL_HI_RES exists and
	 * normal scroll events are sent correctly, so skip all the
	 * guesswork.
	 */
	if (discrete == 0) {
		s->fraction = 1.0;
		goto out;
	}

	/* Calculate the angle per single scroll event */
	angle /= discrete;

	/* We only do magic for click angles smaller than 10 degrees */
	if (angle >= 10) {
		s->fraction = 1.0;
		goto out;
	}

	/* Figure out something that gets close to 15 degrees (the general
	 * wheel default) with a number of clicks. This formula gives us
	 * between 12 and and 20 degrees for the range of 1-10. See
	 * https://bugs.freedesktop.org/attachment.cgi?id=128256 for a
	 * graph.
	 */
	f = round(15.0/angle);

	s->fraction = f;

out:
	return s->dist/s->fraction * discrete;
}

static inline bool
calculate_axis_value(struct xf86libinput *driver_data,
		     enum libinput_pointer_axis axis,
		     struct libinput_event_pointer *event,
		     double *value_out)
{
	enum libinput_pointer_axis_source source;
	double value;

	if (!libinput_event_pointer_has_axis(event, axis))
		return false;

	source = libinput_event_pointer_get_axis_source(event);
	if (source == LIBINPUT_POINTER_AXIS_SOURCE_WHEEL) {
		value = get_wheel_scroll_value(driver_data, event, axis);
	} else {
		double dist = driver_data->options.scroll_pixel_distance;
		assert(dist != 0.0);

		value = libinput_event_pointer_get_axis_value(event, axis);
		/* We need to scale this value into our scroll increment range
		 * because that one is constant for the lifetime of the
		 * device. The user may change the ScrollPixelDistance
		 * though, so where we have a dist of 10 but an increment of
		 * 15, we need to scale from 0..10 into 0..15.
		 */
		value = value/dist * SCROLL_INCREMENT;
	}

	*value_out = value;

	return true;
}

static void
xf86libinput_handle_axis(InputInfoPtr pInfo, struct libinput_event_pointer *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	double value;
	enum libinput_pointer_axis_source source;

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	valuator_mask_zero(mask);

	source = libinput_event_pointer_get_axis_source(event);
	switch(source) {
		case LIBINPUT_POINTER_AXIS_SOURCE_FINGER:
		case LIBINPUT_POINTER_AXIS_SOURCE_WHEEL:
		case LIBINPUT_POINTER_AXIS_SOURCE_CONTINUOUS:
			break;
		default:
			return;
	}

	if (calculate_axis_value(driver_data,
				 LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL,
				 event,
				 &value))
		valuator_mask_set_double(mask, 3, value);

	if (!driver_data->options.horiz_scrolling_enabled)
		goto out;

	if (calculate_axis_value(driver_data,
				 LIBINPUT_POINTER_AXIS_SCROLL_HORIZONTAL,
				 event,
				 &value))
		valuator_mask_set_double(mask, 2, value);

out:
	xf86PostMotionEventM(dev, Relative, mask);
}

static void
xf86libinput_handle_touch(InputInfoPtr pInfo,
			  struct libinput_event_touch *event,
			  enum libinput_event_type event_type)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	int type;
	int slot;
	ValuatorMask *m = driver_data->valuators;
	double val;

	/* libinput doesn't give us hw touch ids which X expects, so
	   emulate them here */
	static unsigned int next_touchid;
	static unsigned int touchids[TOUCH_MAX_SLOTS] = {0};

	if ((driver_data->capabilities & CAP_TOUCH) == 0)
		return;

	slot = libinput_event_touch_get_seat_slot(event);

	switch (event_type) {
		case LIBINPUT_EVENT_TOUCH_DOWN:
			type = XI_TouchBegin;
			touchids[slot] = next_touchid++;
			break;
		case LIBINPUT_EVENT_TOUCH_UP:
		case LIBINPUT_EVENT_TOUCH_CANCEL:
			type = XI_TouchEnd;
			break;
		case LIBINPUT_EVENT_TOUCH_MOTION:
			type = XI_TouchUpdate;
			break;
		default:
			return;
	}

	valuator_mask_zero(m);

	if (type != XI_TouchEnd) {
		val = libinput_event_touch_get_x_transformed(event, TOUCH_AXIS_MAX);
		valuator_mask_set_double(m, 0, val);

		val = libinput_event_touch_get_y_transformed(event, TOUCH_AXIS_MAX);
		valuator_mask_set_double(m, 1, val);
	}

	xf86PostTouchEvent(dev, touchids[slot], type, 0, m);
}

static InputInfoPtr
xf86libinput_pick_device(struct xf86libinput_device *shared_device,
			 struct libinput_event *event)
{
	struct xf86libinput *driver_data;
	uint32_t needed_cap;
	enum libinput_event_type type = libinput_event_get_type(event);

	if (shared_device == NULL)
		return NULL;

	switch(type) {
	case LIBINPUT_EVENT_KEYBOARD_KEY:
		needed_cap = CAP_KEYBOARD;
		break;
	case LIBINPUT_EVENT_TABLET_TOOL_PROXIMITY:
		needed_cap = CAP_TABLET;
		break;
	case LIBINPUT_EVENT_TABLET_TOOL_BUTTON:
	case LIBINPUT_EVENT_TABLET_TOOL_AXIS:
	case LIBINPUT_EVENT_TABLET_TOOL_TIP:
		needed_cap = CAP_TABLET_TOOL;
		break;
	default:
		needed_cap = ~CAP_KEYBOARD;
		break;
	}

	xorg_list_for_each_entry(driver_data,
				 &shared_device->device_list,
				 shared_device_link) {
		if (driver_data->capabilities & needed_cap) {
			struct libinput_tablet_tool *tool;

			if (needed_cap != CAP_TABLET_TOOL)
				return driver_data->pInfo;

			tool = libinput_event_tablet_tool_get_tool(
					   libinput_event_get_tablet_tool_event(event));
			if (libinput_tablet_tool_get_serial(driver_data->tablet_tool) ==
			    libinput_tablet_tool_get_serial(tool) &&
			    libinput_tablet_tool_get_tool_id(driver_data->tablet_tool) ==
			    libinput_tablet_tool_get_tool_id(tool) &&
			    libinput_tablet_tool_get_type(driver_data->tablet_tool) ==
			    libinput_tablet_tool_get_type(tool))
				return driver_data->pInfo;
		}
	}

	return NULL;
}

static void
xf86libinput_tool_destroy_queued_event(struct xf86libinput_tablet_tool_queued_event *qe)
{
	struct libinput_event *e;

	e = libinput_event_tablet_tool_get_base_event(qe->event);
	libinput_event_destroy(e);
	xorg_list_del(&qe->node);
	free(qe);
}

static void
xf86libinput_tool_replay_events(struct xf86libinput_tablet_tool_event_queue *queue)
{
	struct xf86libinput_tablet_tool_queued_event *qe, *tmp;

	xorg_list_for_each_entry_safe(qe, tmp, &queue->event_list, node) {
		struct libinput_event *e;

		e = libinput_event_tablet_tool_get_base_event(qe->event);
		xf86libinput_handle_event(e);
		xf86libinput_tool_destroy_queued_event(qe);
	}
}

static bool
xf86libinput_tool_queue_event(struct libinput_event_tablet_tool *event)
{
	struct libinput_event *e;
	struct libinput_tablet_tool *tool;
	struct xf86libinput_tablet_tool_event_queue *queue;
	struct xf86libinput_tablet_tool_queued_event *qe;

	tool = libinput_event_tablet_tool_get_tool(event);
	if (!tool)
		return true;

	queue = libinput_tablet_tool_get_user_data(tool);
	if (!queue)
		return false;

	if (!queue->need_to_queue) {
		if (!xorg_list_is_empty(&queue->event_list)) {
			libinput_tablet_tool_set_user_data(tool, NULL);
			xf86libinput_tool_replay_events(queue);
			free(queue);
		}

		return false;
	}

	/* We got the prox out while still queuing, just ditch the whole
	 * series of events and the event queue with it. */
	if (libinput_event_tablet_tool_get_proximity_state(event) ==
	    LIBINPUT_TABLET_TOOL_PROXIMITY_STATE_OUT) {
		struct xf86libinput_tablet_tool_queued_event *tmp;

		xorg_list_for_each_entry_safe(qe, tmp, &queue->event_list, node)
			xf86libinput_tool_destroy_queued_event(qe);

		libinput_tablet_tool_set_user_data(tool, NULL);
		free(queue);

		/* we destroy the event here but return true
		 * to make sure the event looks like it got queued and the
		 * caller doesn't destroy it for us
		 */
		e = libinput_event_tablet_tool_get_base_event(event);
		libinput_event_destroy(e);
		return true;
	}

	qe = calloc(1, sizeof(*qe));
	if (!qe) {
		e = libinput_event_tablet_tool_get_base_event(event);
		libinput_event_destroy(e);
		return true;
	}

	qe->event = event;
	xorg_list_append(&qe->node, &queue->event_list);

	return true;
}

static enum event_handling
xf86libinput_handle_tablet_tip(InputInfoPtr pInfo,
			       struct libinput_event_tablet_tool *event)
{
	DeviceIntPtr pDev = pInfo->dev;
	enum libinput_tablet_tool_tip_state state;
	const BOOL is_absolute = TRUE;

	if (xf86libinput_tool_queue_event(event))
		return EVENT_QUEUED;

	xf86libinput_post_tablet_motion(pDev->public.devicePrivate, event);

	state = libinput_event_tablet_tool_get_tip_state(event);

	xf86PostButtonEventP(pInfo->dev,
			     is_absolute, 1,
			     state == LIBINPUT_TABLET_TOOL_TIP_DOWN ? 1 : 0,
			     0, 0, NULL);

	return EVENT_HANDLED;
}

static enum event_handling
xf86libinput_handle_tablet_button(InputInfoPtr pInfo,
				  struct libinput_event_tablet_tool *event)
{
	enum libinput_button_state state;
	uint32_t button, b;

	if (xf86libinput_tool_queue_event(event))
		return EVENT_QUEUED;

	button = libinput_event_tablet_tool_get_button(event);
	state = libinput_event_tablet_tool_get_button_state(event);

	b = btn_linux2xorg(button);

	xf86PostButtonEventP(pInfo->dev,
			     TRUE,
			     b,
			     state == LIBINPUT_BUTTON_STATE_PRESSED ? 1 : 0,
			     0, 0, NULL);

	return EVENT_HANDLED;
}

static void
xf86libinput_apply_area(InputInfoPtr pInfo, double *x, double *y)
{
	struct xf86libinput *driver_data = pInfo->private;
	const struct scale_factor *f = &driver_data->area_scale_factor;
	double sx, sy;

	if (driver_data->options.area.x == 0)
		return;

	/* In left-handed mode, libinput already gives us transformed
	 * coordinates, so we can clip the same way. */

	sx = min(*x * f->x, TABLET_AXIS_MAX);
	sy = min(*y * f->y, TABLET_AXIS_MAX);

	*x = sx;
	*y = sy;
}

static void
xf86libinput_post_tablet_motion(InputInfoPtr pInfo,
				struct libinput_event_tablet_tool *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	struct libinput_tablet_tool *tool;
	double value;
	double x, y;

	x = libinput_event_tablet_tool_get_x_transformed(event,
							 TABLET_AXIS_MAX);
	y = libinput_event_tablet_tool_get_y_transformed(event,
							 TABLET_AXIS_MAX);
	xf86libinput_apply_area(pInfo, &x, &y);
	valuator_mask_set_double(mask, 0, x);
	valuator_mask_set_double(mask, 1, y);

	tool = libinput_event_tablet_tool_get_tool(event);

	if (libinput_tablet_tool_has_pressure(tool)) {
		value = TABLET_PRESSURE_AXIS_MAX * libinput_event_tablet_tool_get_pressure(event);
		if (driver_data->pressurecurve.values)
			value = driver_data->pressurecurve.values[(int)value];
		valuator_mask_set_double(mask, 2, value);
	}

	if (libinput_tablet_tool_has_tilt(tool)) {
		value = libinput_event_tablet_tool_get_tilt_x(event);
		valuator_mask_set_double(mask, 3, value);

		value = libinput_event_tablet_tool_get_tilt_y(event);
		valuator_mask_set_double(mask, 4, value);
	}

	if (libinput_tablet_tool_has_slider(tool)) {
		value = libinput_event_tablet_tool_get_slider_position(event);
		value *= TABLET_AXIS_MAX;
		valuator_mask_set_double(mask, 5, value);
	}

	if (libinput_tablet_tool_has_rotation(tool)) {
		int valuator;

		value = libinput_event_tablet_tool_get_rotation(event);
		value *= TABLET_AXIS_MAX;

		switch (libinput_tablet_tool_get_type(tool)) {
		case LIBINPUT_TABLET_TOOL_TYPE_PEN:
		case LIBINPUT_TABLET_TOOL_TYPE_ERASER:
			valuator = 5;
			break;
		case LIBINPUT_TABLET_TOOL_TYPE_MOUSE:
		case LIBINPUT_TABLET_TOOL_TYPE_LENS:
			valuator = 3;
			break;
		default:
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Invalid rotation axis on tool\n");
			return;
		}

		valuator_mask_set_double(mask, valuator, value);
	}

	xf86PostMotionEventM(dev, Absolute, mask);
}

static enum event_handling
xf86libinput_handle_tablet_axis(InputInfoPtr pInfo,
				struct libinput_event_tablet_tool *event)
{
	if (xf86libinput_tool_queue_event(event))
		return EVENT_QUEUED;

	xf86libinput_post_tablet_motion(pInfo, event);

	return EVENT_HANDLED;
}

static inline const char *
tool_type_to_str(enum libinput_tablet_tool_type type)
{
	const char *str;

	switch (type) {
	case LIBINPUT_TABLET_TOOL_TYPE_PEN: str = "Pen"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_BRUSH: str = "Brush"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_PENCIL: str = "Pencil"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_AIRBRUSH: str = "Airbrush"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_ERASER: str = "Eraser"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_MOUSE: str = "Mouse"; break;
	case LIBINPUT_TABLET_TOOL_TYPE_LENS: str = "Lens"; break;
	default:
		str = "unknown tool";
		break;
	}

	return str;
}

static inline void
xf86libinput_create_tool_subdevice(InputInfoPtr pInfo,
				   struct libinput_event_tablet_tool *event)
{
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;
	struct xf86libinput_tablet_tool *t;
	struct xf86libinput_tablet_tool_event_queue *queue;
	struct libinput_tablet_tool *tool;
	enum libinput_tablet_tool_type tool_type;
	uint64_t serial, tool_id;
	XF86OptionPtr options = NULL;
	char name[64];

	t = calloc(1, sizeof *t);
	if (!t)
		return;

	queue = calloc(1, sizeof(*queue));
	if (!queue) {
		free(t);
		return;
	}
	queue->need_to_queue = true;
	xorg_list_init(&queue->event_list);

	tool = libinput_event_tablet_tool_get_tool(event);
	serial = libinput_tablet_tool_get_serial(tool);
	tool_id = libinput_tablet_tool_get_tool_id(tool);
	tool_type = libinput_tablet_tool_get_type(tool);

	t->tool = libinput_tablet_tool_ref(tool);
	xorg_list_append(&t->node, &shared_device->unclaimed_tablet_tool_list);

	options = xf86ReplaceIntOption(options, "_libinput/tablet-tool-serial", serial);
	options = xf86ReplaceIntOption(options, "_libinput/tablet-tool-id", tool_id);
	options = xf86ReplaceIntOption(options, "_libinput/tablet-tool-type", tool_type);
	/* Convert the name to "<base name> <tool type> (serial number)" */
	if (snprintf(name,
		     sizeof(name),
		     "%s %s (%#x)",
		     pInfo->name,
		     tool_type_to_str(libinput_tablet_tool_get_type(tool)),
		     (uint32_t)serial) > strlen(pInfo->name))
		options = xf86ReplaceStrOption(options, "Name", name);

	libinput_tablet_tool_set_user_data(tool, queue);
	xf86libinput_tool_queue_event(event);

	xf86libinput_create_subdevice(pInfo, CAP_TABLET_TOOL, options);
}

static inline DeviceIntPtr
xf86libinput_find_device_for_tool(InputInfoPtr pInfo,
				  struct libinput_tablet_tool *tool)
{
	struct xf86libinput *dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;
	uint64_t serial = libinput_tablet_tool_get_serial(tool);
	uint64_t tool_id = libinput_tablet_tool_get_tool_id(tool);
	enum libinput_tablet_tool_type tool_type = libinput_tablet_tool_get_type(tool);

	xorg_list_for_each_entry(dev,
				 &shared_device->device_list,
				 shared_device_link) {
		if (dev->tablet_tool &&
		    libinput_tablet_tool_get_serial(dev->tablet_tool) == serial &&
		    libinput_tablet_tool_get_tool_id(dev->tablet_tool) == tool_id &&
		    libinput_tablet_tool_get_type(dev->tablet_tool) == tool_type) {
			return dev->pInfo->dev;
		}
	}

	return NULL;
}

static enum event_handling
xf86libinput_handle_tablet_proximity(InputInfoPtr pInfo,
				     struct libinput_event_tablet_tool *event)
{
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_tablet_tool *tool;
	DeviceIntPtr pDev;
	ValuatorMask *mask = driver_data->valuators;
	double x, y;
	BOOL in_prox;

	tool = libinput_event_tablet_tool_get_tool(event);
	pDev = xf86libinput_find_device_for_tool(pInfo, tool);

	in_prox = libinput_event_tablet_tool_get_proximity_state(event) ==
				LIBINPUT_TABLET_TOOL_PROXIMITY_STATE_IN;

	if (pDev == NULL && in_prox) {
		xf86libinput_create_tool_subdevice(pInfo, event);
		return EVENT_QUEUED;
	}

	if (xf86libinput_tool_queue_event(event))
		return EVENT_QUEUED;

	BUG_RETURN_VAL(pDev == NULL, EVENT_HANDLED);

	x = libinput_event_tablet_tool_get_x_transformed(event, TABLET_AXIS_MAX);
	y = libinput_event_tablet_tool_get_y_transformed(event, TABLET_AXIS_MAX);
	valuator_mask_set_double(mask, 0, x);
	valuator_mask_set_double(mask, 1, y);

	xf86PostProximityEventM(pDev, in_prox, mask);

	/* We have to send an extra motion event after proximity to make
	 * sure the client got the updated x/y coordinates, especially if
	 * they don't handle proximity events (XI2).
	 */
	if (in_prox)
		xf86libinput_post_tablet_motion(pDev->public.devicePrivate, event);

	return EVENT_HANDLED;
}

static void
xf86libinput_handle_tablet_pad_button(InputInfoPtr pInfo,
				      struct libinput_event_tablet_pad *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_tablet_pad_mode_group *group;
	int button, b;
	int is_press;

	if ((driver_data->capabilities & CAP_TABLET_PAD) == 0)
		return;

	b = libinput_event_tablet_pad_get_button_number(event);
	button = 1 + b;
	if (button > 3)
		button += 4; /* offset by scroll buttons */
	is_press = (libinput_event_tablet_pad_get_button_state(event) == LIBINPUT_BUTTON_STATE_PRESSED);

	xf86PostButtonEvent(dev, Relative, button, is_press, 0, 0);

	group = libinput_event_tablet_pad_get_mode_group(event);
	if (libinput_tablet_pad_mode_group_button_is_toggle(group, b))
		update_mode_prop(pInfo, event);
}

static void
xf86libinput_handle_tablet_pad_strip(InputInfoPtr pInfo,
				     struct libinput_event_tablet_pad *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	double value;
	int axis = 3;
	int v;

	if ((driver_data->capabilities & CAP_TABLET_PAD) == 0)
		return;

	/* this isn't compatible with the wacom driver which just forwards
	 * the values and lets the clients handle them with log2. */
	axis += libinput_event_tablet_pad_get_strip_number(event);
	value = libinput_event_tablet_pad_get_strip_position(event);
	v = TABLET_STRIP_AXIS_MAX * value;

	valuator_mask_zero(mask);
	valuator_mask_set(mask, axis, v);

	xf86PostMotionEventM(dev, Absolute, mask);
}

static void
xf86libinput_handle_tablet_pad_ring(InputInfoPtr pInfo,
				     struct libinput_event_tablet_pad *event)
{
	DeviceIntPtr dev = pInfo->dev;
	struct xf86libinput *driver_data = pInfo->private;
	ValuatorMask *mask = driver_data->valuators;
	double value;
	int axis = 5;
	int v;

	if ((driver_data->capabilities & CAP_TABLET_PAD) == 0)
		return;

	axis += libinput_event_tablet_pad_get_ring_number(event);
	value = libinput_event_tablet_pad_get_ring_position(event)/360.0;
	v = TABLET_RING_AXIS_MAX * value;

	valuator_mask_zero(mask);
	valuator_mask_set(mask, axis, v);

	xf86PostMotionEventM(dev, Absolute, mask);
}

static enum event_handling
xf86libinput_handle_event(struct libinput_event *event)
{
	struct libinput_device *device;
	enum libinput_event_type type;
	InputInfoPtr pInfo;
	enum event_handling event_handling = EVENT_HANDLED;

	type = libinput_event_get_type(event);
	device = libinput_event_get_device(event);
	pInfo = xf86libinput_pick_device(libinput_device_get_user_data(device),
					 event);

	if (!pInfo || !pInfo->dev->public.on)
		goto out;

	switch (type) {
		case LIBINPUT_EVENT_NONE:
		case LIBINPUT_EVENT_DEVICE_ADDED:
		case LIBINPUT_EVENT_DEVICE_REMOVED:
			break;
		case LIBINPUT_EVENT_POINTER_MOTION_ABSOLUTE:
			xf86libinput_handle_absmotion(pInfo,
						      libinput_event_get_pointer_event(event));
			break;

		case LIBINPUT_EVENT_POINTER_MOTION:
			xf86libinput_handle_motion(pInfo,
						   libinput_event_get_pointer_event(event));
			break;
		case LIBINPUT_EVENT_POINTER_BUTTON:
			xf86libinput_handle_button(pInfo,
						   libinput_event_get_pointer_event(event));
			break;
		case LIBINPUT_EVENT_KEYBOARD_KEY:
			xf86libinput_handle_key(pInfo,
						libinput_event_get_keyboard_event(event));
			break;
		case LIBINPUT_EVENT_POINTER_AXIS:
			xf86libinput_handle_axis(pInfo,
						 libinput_event_get_pointer_event(event));
			break;
		case LIBINPUT_EVENT_TOUCH_FRAME:
			break;
		case LIBINPUT_EVENT_TOUCH_UP:
		case LIBINPUT_EVENT_TOUCH_DOWN:
		case LIBINPUT_EVENT_TOUCH_MOTION:
		case LIBINPUT_EVENT_TOUCH_CANCEL:
			xf86libinput_handle_touch(pInfo,
						  libinput_event_get_touch_event(event),
						  libinput_event_get_type(event));
			break;
		case LIBINPUT_EVENT_GESTURE_SWIPE_BEGIN:
		case LIBINPUT_EVENT_GESTURE_SWIPE_UPDATE:
		case LIBINPUT_EVENT_GESTURE_SWIPE_END:
		case LIBINPUT_EVENT_GESTURE_PINCH_BEGIN:
		case LIBINPUT_EVENT_GESTURE_PINCH_UPDATE:
		case LIBINPUT_EVENT_GESTURE_PINCH_END:
			break;
		case LIBINPUT_EVENT_TABLET_TOOL_AXIS:
			event_handling = xf86libinput_handle_tablet_axis(pInfo,
							libinput_event_get_tablet_tool_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_TOOL_BUTTON:
			event_handling = xf86libinput_handle_tablet_button(pInfo,
							  libinput_event_get_tablet_tool_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_TOOL_PROXIMITY:
			event_handling = xf86libinput_handle_tablet_proximity(pInfo,
							     libinput_event_get_tablet_tool_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_TOOL_TIP:
			event_handling = xf86libinput_handle_tablet_tip(pInfo,
						       libinput_event_get_tablet_tool_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_PAD_BUTTON:
			xf86libinput_handle_tablet_pad_button(pInfo,
							      libinput_event_get_tablet_pad_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_PAD_RING:
			xf86libinput_handle_tablet_pad_ring(pInfo,
							    libinput_event_get_tablet_pad_event(event));
			break;
		case LIBINPUT_EVENT_TABLET_PAD_STRIP:
			xf86libinput_handle_tablet_pad_strip(pInfo,
							     libinput_event_get_tablet_pad_event(event));
			break;
		case LIBINPUT_EVENT_SWITCH_TOGGLE:
			break;
	}

out:
	return event_handling;
}

static void
xf86libinput_read_input(InputInfoPtr pInfo)
{
	struct libinput *libinput = driver_context.libinput;
	int rc;
	struct libinput_event *event;

        rc = libinput_dispatch(libinput);
	if (rc == -EAGAIN)
		return;

	if (rc < 0) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Error reading events: %s\n",
			    strerror(-rc));
		return;
	}

	while ((event = libinput_get_event(libinput))) {
		if (xf86libinput_handle_event(event) == EVENT_HANDLED)
			libinput_event_destroy(event);
	}
}

/*
   libinput provides a userdata for the context, but not per path device. so
   the open_restricted call has the libinput context, but no reference to
   the pInfo->fd that we actually need to return.
   The server stores the fd in the options though, so we just get it from
   there. If a device is added twice with two different fds this may give us
   the wrong fd but why are you doing that anyway.
 */
static int
open_restricted(const char *path, int flags, void *data)
{
	InputInfoPtr pInfo;
	int fd = -1;

	/* Special handling for sysfs files (used for pad LEDs) */
	if (strneq(path, "/sys/", 5)) {
		fd = open(path, flags);
		return fd < 0 ? -errno : fd;
	}

	nt_list_for_each_entry(pInfo, xf86FirstLocalDevice(), next) {
		char *device = xf86CheckStrOption(pInfo->options, "Device", NULL);

		if (device != NULL && streq(path, device)) {
			free(device);
			break;
		}
		free(device);
	}

	if (pInfo == NULL) {
		xf86Msg(X_ERROR, "Failed to look up path '%s'\n", path);
		return -ENODEV;
	}

	fd = xf86OpenSerial(pInfo->options);
	if (fd < 0)
		return -errno;

	xf86FlushInput(fd);

	return fd;
}

static void
close_restricted(int fd, void *data)
{
	InputInfoPtr pInfo;
	int server_fd = -1;
	BOOL found = FALSE;

	nt_list_for_each_entry(pInfo, xf86FirstLocalDevice(), next) {
		server_fd = xf86CheckIntOption(pInfo->options, "fd", -1);

		if (server_fd == fd) {
			found = TRUE;
			break;
		}
	}

	if (!found)
		xf86CloseSerial(fd);
}

const struct libinput_interface interface = {
    .open_restricted = open_restricted,
    .close_restricted = close_restricted,
};

_X_ATTRIBUTE_PRINTF(3, 0)
static void
xf86libinput_log_handler(struct libinput *libinput,
			 enum libinput_log_priority priority,
			 const char *format,
			 va_list args)
{
	MessageType type;
	int verbosity;

	switch(priority) {
	case LIBINPUT_LOG_PRIORITY_DEBUG:
		type = X_DEBUG;
		verbosity = 10;
		break;
	case LIBINPUT_LOG_PRIORITY_ERROR:
		type = X_ERROR;
		verbosity = -1;
		break;
	case LIBINPUT_LOG_PRIORITY_INFO:
		type = X_INFO;
		verbosity = 3;
		break;
	default:
		return;
	}

	/* log messages in libinput are per-context, not per device, so we
	   can't use xf86IDrvMsg here, and the server has no xf86VMsg or
	   similar */
	LogVMessageVerb(type, verbosity, format, args);
}

static inline BOOL
xf86libinput_parse_tap_option(InputInfoPtr pInfo,
			      struct libinput_device *device)
{
	BOOL tap;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return FALSE;

	tap = xf86SetBoolOption(pInfo->options,
				"Tapping",
				libinput_device_config_tap_get_enabled(device));

	if (libinput_device_config_tap_set_enabled(device, tap) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping to %d\n",
			    tap);
		tap = libinput_device_config_tap_get_enabled(device);
	}

	return tap;
}

static inline BOOL
xf86libinput_parse_tap_drag_option(InputInfoPtr pInfo,
				   struct libinput_device *device)
{
	BOOL drag;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return FALSE;

	drag = xf86SetBoolOption(pInfo->options,
				 "TappingDrag",
				 libinput_device_config_tap_get_drag_enabled(device));

	if (libinput_device_config_tap_set_drag_enabled(device, drag) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping Drag Lock to %d\n",
			    drag);
		drag = libinput_device_config_tap_get_drag_enabled(device);
	}

	return drag;
}

static inline BOOL
xf86libinput_parse_tap_drag_lock_option(InputInfoPtr pInfo,
					struct libinput_device *device)
{
	BOOL drag_lock;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return FALSE;

	drag_lock = xf86SetBoolOption(pInfo->options,
				      "TappingDragLock",
				      libinput_device_config_tap_get_drag_lock_enabled(device));

	if (libinput_device_config_tap_set_drag_lock_enabled(device, drag_lock) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping Drag Lock to %d\n",
			    drag_lock);
		drag_lock = libinput_device_config_tap_get_drag_lock_enabled(device);
	}

	return drag_lock;
}

static inline enum libinput_config_tap_button_map
xf86libinput_parse_tap_buttonmap_option(InputInfoPtr pInfo,
					struct libinput_device *device)
{
	enum libinput_config_tap_button_map map;
	char *str;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return FALSE;

	map = libinput_device_config_tap_get_button_map(device);
	str = xf86SetStrOption(pInfo->options,
			       "TappingButtonMap",
			       NULL);
	if (str) {
		if (streq(str, "lmr"))
			map = LIBINPUT_CONFIG_TAP_MAP_LMR;
		else if (streq(str, "lrm"))
			map = LIBINPUT_CONFIG_TAP_MAP_LRM;
		else
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Invalid TapButtonMap: %s\n",
				    str);
		free(str);
	}

	if (libinput_device_config_tap_set_button_map(device, map) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set Tapping Button Map to %d\n",
			    map);
		map = libinput_device_config_tap_get_button_map(device);
	}

	return map;
}

static inline double
xf86libinput_parse_accel_option(InputInfoPtr pInfo,
				struct libinput_device *device)
{
	double speed;

	if (!libinput_device_config_accel_is_available(device))
		return 0.0;

	speed = xf86SetRealOption(pInfo->options,
				  "AccelSpeed",
				  libinput_device_config_accel_get_speed(device));
	if (libinput_device_config_accel_set_speed(device, speed) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Invalid speed %.2f, using 0 instead\n",
			    speed);
		speed = libinput_device_config_accel_get_speed(device);
	}

	return speed;
}

static inline enum libinput_config_accel_profile
xf86libinput_parse_accel_profile_option(InputInfoPtr pInfo,
					struct libinput_device *device)
{
	enum libinput_config_accel_profile profile;
	char *str;

	if (libinput_device_config_accel_get_profiles(device) ==
	    LIBINPUT_CONFIG_ACCEL_PROFILE_NONE)
		return LIBINPUT_CONFIG_ACCEL_PROFILE_NONE;

	str = xf86SetStrOption(pInfo->options, "AccelProfile", NULL);
	if (!str)
		profile = libinput_device_config_accel_get_profile(device);
	else if (strncasecmp(str, "adaptive", 9) == 0)
		profile = LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE;
	else if (strncasecmp(str, "flat", 4) == 0)
		profile = LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT;
	else {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Unknown accel profile '%s'. Using default.\n",
			    str);
		profile = libinput_device_config_accel_get_profile(device);
	}

	free(str);

	return profile;
}

static inline BOOL
xf86libinput_parse_natscroll_option(InputInfoPtr pInfo,
				    struct libinput_device *device)
{
	BOOL natural_scroll;

	if (!libinput_device_config_scroll_has_natural_scroll(device))
		return FALSE;

	natural_scroll = xf86SetBoolOption(pInfo->options,
					   "NaturalScrolling",
					   libinput_device_config_scroll_get_natural_scroll_enabled(device));
	if (libinput_device_config_scroll_set_natural_scroll_enabled(device,
								     natural_scroll) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set NaturalScrolling to %d\n",
			    natural_scroll);

		natural_scroll = libinput_device_config_scroll_get_natural_scroll_enabled(device);
	}

	return natural_scroll;
}

static inline enum libinput_config_send_events_mode
xf86libinput_parse_sendevents_option(InputInfoPtr pInfo,
				     struct libinput_device *device)
{
	char *modestr;
	enum libinput_config_send_events_mode mode;

	if (libinput_device_config_send_events_get_modes(device) == LIBINPUT_CONFIG_SEND_EVENTS_ENABLED)
		return LIBINPUT_CONFIG_SEND_EVENTS_ENABLED;

	mode = libinput_device_config_send_events_get_mode(device);
	modestr = xf86SetStrOption(pInfo->options,
				   "SendEventsMode",
				   NULL);
	if (modestr) {
		if (streq(modestr, "enabled"))
			mode = LIBINPUT_CONFIG_SEND_EVENTS_ENABLED;
		else if (streq(modestr, "disabled"))
			mode = LIBINPUT_CONFIG_SEND_EVENTS_DISABLED;
		else if (streq(modestr, "disabled-on-external-mouse"))
			mode = LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE;
		else
			xf86IDrvMsg(pInfo, X_ERROR,
				    "Invalid SendeventsMode: %s\n",
				    modestr);
		free(modestr);
	}

	if (libinput_device_config_send_events_set_mode(device, mode) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set SendEventsMode %u\n", mode);
		mode = libinput_device_config_send_events_get_mode(device);
	}

	return mode;
}

static inline void
xf86libinput_parse_calibration_option(InputInfoPtr pInfo,
				      struct libinput_device *device,
				      float matrix_out[9])
{
	char *str;
	float matrix[9] = { 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0};
	int num_calibration;

	memcpy(matrix_out, matrix, sizeof(matrix));

	if (!libinput_device_config_calibration_has_matrix(device))
		return;

	libinput_device_config_calibration_get_matrix(device, matrix);
	memcpy(matrix_out, matrix, sizeof(matrix));

	str = xf86SetStrOption(pInfo->options,
			       "CalibrationMatrix",
			       NULL);
	if (!str)
		return;

	num_calibration = sscanf(str, "%f %f %f %f %f %f %f %f %f ",
				 &matrix[0], &matrix[1],
				 &matrix[2], &matrix[3],
				 &matrix[4], &matrix[5],
				 &matrix[6], &matrix[7],
				 &matrix[8]);
	if (num_calibration != 9) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Invalid matrix: %s, using default\n",  str);
	} else if (libinput_device_config_calibration_set_matrix(device,
								 matrix) ==
		   LIBINPUT_CONFIG_STATUS_SUCCESS) {
		memcpy(matrix_out, matrix, sizeof(matrix));
	} else
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to apply matrix: %s, using default\n",  str);
	free(str);
}

static inline BOOL
xf86libinput_parse_lefthanded_option(InputInfoPtr pInfo,
				     struct libinput_device *device)
{
	BOOL left_handed;

	if (!libinput_device_config_left_handed_is_available(device))
		return FALSE;

	left_handed = xf86SetBoolOption(pInfo->options,
					"LeftHanded",
					libinput_device_config_left_handed_get(device));
	if (libinput_device_config_left_handed_set(device,
						   left_handed) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set LeftHanded to %d\n",
			    left_handed);
		left_handed = libinput_device_config_left_handed_get(device);
	}

	return left_handed;
}

static inline enum libinput_config_scroll_method
xf86libinput_parse_scroll_option(InputInfoPtr pInfo,
				 struct libinput_device *device)
{
	uint32_t scroll_methods;
	enum libinput_config_scroll_method m;
	char *method;

	scroll_methods = libinput_device_config_scroll_get_methods(device);
	if (scroll_methods == LIBINPUT_CONFIG_SCROLL_NO_SCROLL)
		return LIBINPUT_CONFIG_SCROLL_NO_SCROLL;

	method = xf86SetStrOption(pInfo->options, "ScrollMethod", NULL);
	if (!method)
		m = libinput_device_config_scroll_get_method(device);
	else if (strncasecmp(method, "twofinger", 9) == 0)
		m = LIBINPUT_CONFIG_SCROLL_2FG;
	else if (strncasecmp(method, "edge", 4) == 0)
		m = LIBINPUT_CONFIG_SCROLL_EDGE;
	else if (strncasecmp(method, "button", 6) == 0)
		m = LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN;
	else if (strncasecmp(method, "none", 4) == 0)
		m = LIBINPUT_CONFIG_SCROLL_NO_SCROLL;
	else {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Unknown scroll method '%s'. Using default.\n",
			    method);
		m = libinput_device_config_scroll_get_method(device);
	}

	free(method);
	return m;
}

static inline unsigned int
xf86libinput_parse_scrollbutton_option(InputInfoPtr pInfo,
				       struct libinput_device *device)
{
	unsigned int b;
	CARD32 scroll_button;

	if ((libinput_device_config_scroll_get_methods(device) &
	    LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN) == 0)
		return 0;

	b = btn_linux2xorg(libinput_device_config_scroll_get_button(device));
	scroll_button = xf86SetIntOption(pInfo->options,
					 "ScrollButton",
					 b);

	b = btn_xorg2linux(scroll_button);

	if (libinput_device_config_scroll_set_button(device,
						     b) != LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set ScrollButton to %u\n",
			    scroll_button);
		scroll_button = btn_linux2xorg(libinput_device_config_scroll_get_button(device));
	}
	return scroll_button;
}

static inline BOOL
xf86libinput_parse_scrollbuttonlock_option(InputInfoPtr pInfo,
					   struct libinput_device *device)
{
	bool dflt;
	BOOL buttonlock = FALSE;

	if ((libinput_device_config_scroll_get_methods(device) &
	    LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN) == 0)
		return 0;

#if HAVE_LIBINPUT_SCROLL_BUTTON_LOCK
	dflt = libinput_device_config_scroll_get_default_button_lock(device);
	buttonlock = xf86SetBoolOption(pInfo->options, "ScrollButtonLock", dflt);

	if (libinput_device_config_scroll_set_button_lock(device, buttonlock)
						     != LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to %s ScrollButtonLock\n",
			    buttonlock ? "enable" : "disable");
		buttonlock = libinput_device_config_scroll_get_button_lock(device);
	}
#endif
	return buttonlock;
}

static inline bool
xf86libinput_want_scroll_distance_option(struct libinput_device *device)
{
	uint32_t methods =
	    LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN |
	    LIBINPUT_CONFIG_SCROLL_2FG |
	    LIBINPUT_CONFIG_SCROLL_EDGE;

	if ((libinput_device_config_scroll_get_methods(device) & methods) == 0)
		return false;

	return true;
}

static inline uint32_t
xf86libinput_parse_scroll_pixel_distance_option(InputInfoPtr pInfo,
						struct libinput_device *device)
{
	uint32_t dflt = SCROLL_INCREMENT;
	uint32_t dist;

	if (!xf86libinput_want_scroll_distance_option(device))
		return dflt;

	dist = xf86SetIntOption(pInfo->options, "ScrollPixelDistance", dflt);
	if (dist < TOUCHPAD_SCROLL_DIST_MIN || dist > TOUCHPAD_SCROLL_DIST_MAX) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Invalid ScrollPixelDistance %d\n", dist);
		dist = dflt;
	}
	return dist;
}

static inline unsigned int
xf86libinput_parse_clickmethod_option(InputInfoPtr pInfo,
				      struct libinput_device *device)
{
	uint32_t click_methods = libinput_device_config_click_get_methods(device);
	enum libinput_config_click_method m;
	char *method;

	if (click_methods == LIBINPUT_CONFIG_CLICK_METHOD_NONE)
		return LIBINPUT_CONFIG_CLICK_METHOD_NONE;

	method = xf86SetStrOption(pInfo->options, "ClickMethod", NULL);

	if (!method)
		m = libinput_device_config_click_get_method(device);
	else if (strncasecmp(method, "buttonareas", 11) == 0)
		m = LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS;
	else if (strncasecmp(method, "clickfinger", 11) == 0)
		m = LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER;
	else if (strncasecmp(method, "none", 4) == 0)
		m = LIBINPUT_CONFIG_CLICK_METHOD_NONE;
	else {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Unknown click method '%s'. Using default.\n",
			    method);
		m = libinput_device_config_click_get_method(device);
	}
	free(method);

	return m;
}

static inline BOOL
xf86libinput_parse_middleemulation_option(InputInfoPtr pInfo,
					  struct libinput_device *device)
{
	BOOL enabled;

	if (!libinput_device_config_middle_emulation_is_available(device))
		return FALSE;

	enabled = xf86SetBoolOption(pInfo->options,
				    "MiddleEmulation",
				    libinput_device_config_middle_emulation_get_default_enabled(device));
	if (libinput_device_config_middle_emulation_set_enabled(device, enabled) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set MiddleEmulation to %d\n",
			    enabled);
		enabled = libinput_device_config_middle_emulation_get_enabled(device);
	}

	return enabled;
}

static inline BOOL
xf86libinput_parse_disablewhiletyping_option(InputInfoPtr pInfo,
					     struct libinput_device *device)
{
	BOOL enabled;

	if (!libinput_device_config_dwt_is_available(device))
		return FALSE;

	enabled = xf86SetBoolOption(pInfo->options,
				    "DisableWhileTyping",
				    libinput_device_config_dwt_get_default_enabled(device));
	if (libinput_device_config_dwt_set_enabled(device, enabled) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Failed to set DisableWhileTyping to %d\n",
			    enabled);
		enabled = libinput_device_config_dwt_get_enabled(device);
	}

	return enabled;
}

static void
xf86libinput_parse_buttonmap_option(InputInfoPtr pInfo,
				    unsigned char *btnmap,
				    size_t size)
{
	const int MAXBUTTONS = 32;
	char *mapping, *map, *s = NULL;
	int idx = 1;

	init_button_map(btnmap, size);

	mapping = xf86SetStrOption(pInfo->options, "ButtonMapping", NULL);
	if (!mapping)
		return;

	map = mapping;
	do
	{
		unsigned long int btn = strtoul(map, &s, 10);

		if (s == map || btn > MAXBUTTONS)
		{
			xf86IDrvMsg(pInfo, X_ERROR,
				    "... Invalid button mapping. Using defaults\n");
			init_button_map(btnmap, size);
			break;
		}

		btnmap[idx++] = btn;
		map = s;
	} while (s && *s != '\0' && idx < MAXBUTTONS);

	free(mapping);
}

static inline void
xf86libinput_parse_draglock_option(InputInfoPtr pInfo,
				   struct xf86libinput *driver_data)
{
	char *str;

	str = xf86SetStrOption(pInfo->options, "DragLockButtons", NULL);
	if (draglock_init_from_string(&driver_data->draglock, str) != 0)
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Invalid DragLockButtons option: \"%s\"\n",
			    str);
	free(str);
}

static inline BOOL
xf86libinput_parse_horiz_scroll_option(InputInfoPtr pInfo)
{
	return xf86SetBoolOption(pInfo->options, "HorizontalScrolling", TRUE);
}

static inline double
xf86libinput_parse_rotation_angle_option(InputInfoPtr pInfo,
					 struct libinput_device *device)
{
	double angle;

	if (!libinput_device_config_rotation_is_available(device))
		return 0.0;

	angle = xf86SetRealOption(pInfo->options,
				  "RotationAngle",
				  libinput_device_config_rotation_get_default_angle(device));
	if (libinput_device_config_rotation_set_angle(device, angle) !=
	    LIBINPUT_CONFIG_STATUS_SUCCESS) {
		xf86IDrvMsg(pInfo, X_ERROR,
			    "Invalid angle %.2f, using 0.0 instead\n",
			    angle);
		angle = libinput_device_config_rotation_get_angle(device);
	}

	return angle;
}

static void
xf86libinput_parse_pressurecurve_option(InputInfoPtr pInfo,
					struct xf86libinput *driver_data,
					struct bezier_control_point pcurve[4])
{
	struct bezier_control_point controls[4] = {
		{ 0.0, 0.0 },
		{ 0.0, 0.0 },
		{ 1.0, 1.0 },
		{ 1.0, 1.0 },
	};
	float points[8];
	char *str;
	int rc = 0;
	int test_bezier[64];
	struct libinput_tablet_tool *tool = driver_data->tablet_tool;

	if ((driver_data->capabilities & CAP_TABLET_TOOL) == 0)
		return;

	if (!tool || !libinput_tablet_tool_has_pressure(tool))
		return;

	str = xf86SetStrOption(pInfo->options,
			       "TabletToolPressureCurve",
			       NULL);
	if (!str)
		goto out;

	rc = sscanf(str, "%f/%f %f/%f %f/%f %f/%f",
		    &points[0], &points[1], &points[2], &points[3],
		    &points[4], &points[5], &points[6], &points[7]);
	if (rc != 8)
		goto out;

	for (int i = 0; i < 4; i++) {
		if (points[i] < 0.0 || points[i] > 1.0)
			goto out;
	}

	controls[0].x = points[0];
	controls[0].y = points[1];
	controls[1].x = points[2];
	controls[1].y = points[3];
	controls[2].x = points[4];
	controls[2].y = points[5];
	controls[3].x = points[6];
	controls[3].y = points[7];

	if (!cubic_bezier(controls, test_bezier, ARRAY_SIZE(test_bezier))) {
		memcpy(controls, bezier_defaults, sizeof(controls));
		goto out;
	}

	rc = 0;
out:
	if (rc != 0)
		xf86IDrvMsg(pInfo, X_ERROR, "Invalid pressure curve: %s\n",  str);
	free(str);
	memcpy(pcurve, controls, sizeof(controls));
	xf86libinput_set_pressurecurve(driver_data, controls);
}

static inline bool
want_area_handling(struct xf86libinput *driver_data)
{
	struct libinput_device *device = driver_data->shared_device->device;

	if ((driver_data->capabilities & CAP_TABLET_TOOL) == 0)
		return false;

	/* If we have a calibration matrix, it's a built-in tablet and we
	 * don't need to set the area ratio on those */
	return !libinput_device_config_calibration_has_matrix(device);
}

static void
xf86libinput_parse_tablet_area_option(InputInfoPtr pInfo,
				      struct xf86libinput *driver_data,
				      struct ratio *area_out)
{
	char *str;
	int rc;
	struct ratio area;

	if (!want_area_handling(driver_data))
		return;

	str = xf86SetStrOption(pInfo->options,
			       "TabletToolAreaRatio",
			       NULL);
	if (!str || streq(str, "default"))
		goto out;

	rc = sscanf(str, "%d:%d", &area.x, &area.y);
	if (rc != 2 || area.x <= 0 || area.y <= 0) {
		xf86IDrvMsg(pInfo, X_ERROR, "Invalid tablet tool area ratio: %s\n",  str);
	} else {
		*area_out = area;
	}

out:
	free(str);
}

static void
xf86libinput_parse_options(InputInfoPtr pInfo,
			   struct xf86libinput *driver_data,
			   struct libinput_device *device)
{
	struct options *options = &driver_data->options;

	/* libinput options */
	options->tapping = xf86libinput_parse_tap_option(pInfo, device);
	options->tap_drag = xf86libinput_parse_tap_drag_option(pInfo, device);
	options->tap_drag_lock = xf86libinput_parse_tap_drag_lock_option(pInfo, device);
	options->tap_button_map = xf86libinput_parse_tap_buttonmap_option(pInfo, device);
	options->speed = xf86libinput_parse_accel_option(pInfo, device);
	options->accel_profile = xf86libinput_parse_accel_profile_option(pInfo, device);
	options->natural_scrolling = xf86libinput_parse_natscroll_option(pInfo, device);
	options->sendevents = xf86libinput_parse_sendevents_option(pInfo, device);
	options->left_handed = xf86libinput_parse_lefthanded_option(pInfo, device);
	options->scroll_method = xf86libinput_parse_scroll_option(pInfo, device);
	options->scroll_button = xf86libinput_parse_scrollbutton_option(pInfo, device);
	options->scroll_buttonlock = xf86libinput_parse_scrollbuttonlock_option(pInfo, device);
	options->scroll_pixel_distance = xf86libinput_parse_scroll_pixel_distance_option(pInfo, device);
	options->click_method = xf86libinput_parse_clickmethod_option(pInfo, device);
	options->middle_emulation = xf86libinput_parse_middleemulation_option(pInfo, device);
	options->disable_while_typing = xf86libinput_parse_disablewhiletyping_option(pInfo, device);
	options->rotation_angle = xf86libinput_parse_rotation_angle_option(pInfo, device);
	xf86libinput_parse_calibration_option(pInfo, device, driver_data->options.matrix);

	/* non-libinput options */
	xf86libinput_parse_buttonmap_option(pInfo,
					    options->btnmap,
					    sizeof(options->btnmap));
	if (driver_data->capabilities & CAP_POINTER) {
		xf86libinput_parse_draglock_option(pInfo, driver_data);
		options->horiz_scrolling_enabled = xf86libinput_parse_horiz_scroll_option(pInfo);
	}

	xf86libinput_parse_pressurecurve_option(pInfo,
						driver_data,
						options->pressurecurve);
	xf86libinput_parse_tablet_area_option(pInfo,
					      driver_data,
					      &options->area);
}

static const char*
xf86libinput_get_type_name(struct libinput_device *device,
			   struct xf86libinput *driver_data)
{
	const char *type_name;

	/* now pick an actual type */
	if (libinput_device_config_tap_get_finger_count(device) > 0)
		type_name = XI_TOUCHPAD;
	else if (driver_data->capabilities & CAP_TOUCH)
		type_name = XI_TOUCHSCREEN;
	else if (driver_data->capabilities & CAP_POINTER)
		type_name = XI_MOUSE;
	else if (driver_data->capabilities & CAP_TABLET)
		type_name = XI_TABLET;
	else if (driver_data->capabilities & CAP_TABLET_PAD)
		type_name = "PAD";
	else if (driver_data->capabilities & CAP_TABLET_TOOL){
		switch (libinput_tablet_tool_get_type(driver_data->tablet_tool)) {
		case LIBINPUT_TABLET_TOOL_TYPE_PEN:
		case LIBINPUT_TABLET_TOOL_TYPE_BRUSH:
		case LIBINPUT_TABLET_TOOL_TYPE_PENCIL:
		case LIBINPUT_TABLET_TOOL_TYPE_AIRBRUSH:
			type_name = "STYLUS";
			break;
		case LIBINPUT_TABLET_TOOL_TYPE_ERASER:
			type_name = "ERASER";
			break;
		case LIBINPUT_TABLET_TOOL_TYPE_MOUSE:
		case LIBINPUT_TABLET_TOOL_TYPE_LENS:
			type_name = "CURSOR";
			break;
		default:
			type_name = XI_TABLET;
			break;
		}
	} else
		type_name = XI_KEYBOARD;

	return type_name;
}

static void
xf86libinput_init_driver_context(void)
{
	if (!driver_context.libinput) {
		driver_context.libinput = libinput_path_create_context(&interface, &driver_context);
		libinput_log_set_handler(driver_context.libinput,
					 xf86libinput_log_handler);
		/* we want all msgs, let the server filter */
		libinput_log_set_priority(driver_context.libinput,
					  LIBINPUT_LOG_PRIORITY_DEBUG);
	} else {
		libinput_ref(driver_context.libinput);
	}
}

struct xf86libinput_hotplug_info {
	InputAttributes *attrs;
	InputOption *input_options;
};

static DeviceIntPtr
xf86libinput_hotplug_device(struct xf86libinput_hotplug_info *hotplug)
{
	DeviceIntPtr dev;

	input_lock();
	if (NewInputDeviceRequest(hotplug->input_options,
				  hotplug->attrs,
				  &dev) != Success)
		dev = NULL;
	input_unlock();

	input_option_free_list(&hotplug->input_options);
	FreeInputAttributes(hotplug->attrs);
	free(hotplug);

	return dev;
}

static Bool
xf86libinput_hotplug_device_cb(ClientPtr client, pointer closure)
{
	struct xf86libinput_hotplug_info *hotplug = closure;

	xf86libinput_hotplug_device(hotplug);

	return TRUE;
}

static void
xf86libinput_create_subdevice(InputInfoPtr pInfo,
			      uint32_t capabilities,
			      XF86OptionPtr extra_options)
{
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device;
	struct xf86libinput_hotplug_info *hotplug;
	InputOption *iopts = NULL;
	XF86OptionPtr options, o;

	shared_device = driver_data->shared_device;
	pInfo->options = xf86ReplaceIntOption(pInfo->options,
					      "_libinput/shared-device",
					      shared_device->id);

	options = xf86OptionListDuplicate(pInfo->options);
	options = xf86ReplaceStrOption(options, "_source", "_driver/libinput");
	options = xf86OptionListMerge(options, extra_options);

	if (capabilities & CAP_KEYBOARD)
		options = xf86ReplaceBoolOption(options, "_libinput/cap-keyboard", 1);
	if (capabilities & CAP_POINTER)
		options = xf86ReplaceBoolOption(options, "_libinput/cap-pointer", 1);
	if (capabilities & CAP_TOUCH)
		options = xf86ReplaceBoolOption(options, "_libinput/cap-touch", 1);
	if (capabilities & CAP_TABLET_TOOL)
		options = xf86ReplaceBoolOption(options, "_libinput/cap-tablet-tool", 1);
	if (capabilities & CAP_TABLET_PAD)
		options = xf86ReplaceBoolOption(options, "_libinput/cap-tablet-pad", 1);

	/* need convert from one option list to the other. woohoo. */
	o = options;
	while (o) {
		iopts = input_option_new(iopts,
					 xf86OptionName(o),
					 xf86OptionValue(o));
		o = xf86NextOption(o);
	}
	xf86OptionListFree(options);

	hotplug = calloc(1, sizeof(*hotplug));
	if (!hotplug)
		return;

	hotplug->input_options = iopts;
	hotplug->attrs = DuplicateInputAttributes(pInfo->attrs);

	xf86IDrvMsg(pInfo, X_INFO, "needs a virtual subdevice\n");

	QueueWorkProc(xf86libinput_hotplug_device_cb, serverClient, hotplug);
}

static inline uint32_t
caps_from_options(InputInfoPtr pInfo)
{
	uint32_t capabilities = 0;

	if (xf86CheckBoolOption(pInfo->options, "_libinput/cap-keyboard", 0))
		capabilities |= CAP_KEYBOARD;
	if (xf86CheckBoolOption(pInfo->options, "_libinput/cap-pointer", 0))
		capabilities |= CAP_POINTER;
	if (xf86CheckBoolOption(pInfo->options, "_libinput/cap-touch", 0))
		capabilities |= CAP_TOUCH;
	if (xf86CheckBoolOption(pInfo->options, "_libinput/cap-tablet-tool", 0))
		capabilities |= CAP_TABLET_TOOL;

	return capabilities;
}

static inline Bool
claim_tablet_tool(InputInfoPtr pInfo)
{
	struct xf86libinput *driver_data = pInfo->private;
	struct xf86libinput_device *shared_device = driver_data->shared_device;
	struct xf86libinput_tablet_tool_event_queue *queue;
	struct xf86libinput_tablet_tool *t;
	enum libinput_tablet_tool_type tool_type;
	uint64_t serial, tool_id;

	serial = (uint32_t)xf86CheckIntOption(pInfo->options, "_libinput/tablet-tool-serial", 0);
	tool_id = (uint32_t)xf86CheckIntOption(pInfo->options, "_libinput/tablet-tool-id", 0);
	tool_type = (uint32_t)xf86CheckIntOption(pInfo->options, "_libinput/tablet-tool-type", 0);

	xorg_list_for_each_entry(t,
				 &shared_device->unclaimed_tablet_tool_list,
				 node) {
		if (libinput_tablet_tool_get_serial(t->tool) == serial &&
		    libinput_tablet_tool_get_tool_id(t->tool) == tool_id &&
		    libinput_tablet_tool_get_type(t->tool) == tool_type) {
			driver_data->tablet_tool = t->tool;
			queue = libinput_tablet_tool_get_user_data(t->tool);
			if (queue)
				queue->need_to_queue = false;
			xorg_list_del(&t->node);
			free(t);
			return TRUE;
		}
	}

	return FALSE;
}

static int
xf86libinput_pre_init(InputDriverPtr drv,
		      InputInfoPtr pInfo,
		      int flags)
{
	struct xf86libinput *driver_data = NULL;
	struct xf86libinput_device *shared_device = NULL;
	struct libinput *libinput = NULL;
	struct libinput_device *device = NULL;
	char *path = NULL;
	bool is_subdevice;

	pInfo->type_name = 0;
	pInfo->device_control = xf86libinput_device_control;
	pInfo->read_input = xf86libinput_read_input;
	pInfo->control_proc = NULL;
	pInfo->switch_mode = NULL;

	driver_data = calloc(1, sizeof(*driver_data));
	if (!driver_data)
		goto fail;

	driver_data->valuators = valuator_mask_new(6);
	if (!driver_data->valuators)
		goto fail;

	driver_data->valuators_unaccelerated = valuator_mask_new(2);
	if (!driver_data->valuators_unaccelerated)
		goto fail;

	path = xf86SetStrOption(pInfo->options, "Device", NULL);
	if (!path)
		goto fail;

	xf86libinput_init_driver_context();
	libinput = driver_context.libinput;

	if (libinput == NULL) {
		xf86IDrvMsg(pInfo, X_ERROR, "Creating a device for %s failed\n", path);
		goto fail;
	}

	is_subdevice = xf86libinput_is_subdevice(pInfo);
	if (is_subdevice) {
		InputInfoPtr parent;
		struct xf86libinput *parent_driver_data;

		parent = xf86libinput_get_parent(pInfo);
		if (!parent) {
			xf86IDrvMsg(pInfo, X_ERROR, "Failed to find parent device\n");
			goto fail;
		}

		parent_driver_data = parent->private;
		if (!parent_driver_data) /* parent already removed again */
			goto fail;

		xf86IDrvMsg(pInfo, X_INFO, "is a virtual subdevice\n");
		shared_device = xf86libinput_shared_ref(parent_driver_data->shared_device);
		device = shared_device->device;
		if (!device)
			xf86IDrvMsg(pInfo, X_ERROR, "Parent device not available\n");
	}

	if (!device) {
		device = libinput_path_add_device(libinput, path);
		if (!device) {
			xf86IDrvMsg(pInfo, X_ERROR, "Failed to create a device for %s\n", path);
			goto fail;
		}

		/* We ref the device above, then remove it. It get's
		   re-added with the same path in DEVICE_ON, we hope
		   it doesn't change until then */
		libinput_device_ref(device);
		libinput_path_remove_device(device);

		shared_device = xf86libinput_shared_create(device);
		if (!shared_device) {
			libinput_device_unref(device);
			goto fail;
		}
	}

	pInfo->private = driver_data;
	driver_data->pInfo = pInfo;
	driver_data->path = path;
	driver_data->shared_device = shared_device;
	xorg_list_append(&driver_data->shared_device_link,
			 &shared_device->device_list);

	/* Scroll dist value matters for source finger/continuous. For those
	 * devices libinput provides pixel-like data, changing this will
	 * affect touchpad scroll speed. For wheels it doesn't matter as
	 * we're using the discrete value only.
	 */
	driver_data->scroll.v.dist = SCROLL_INCREMENT;
	driver_data->scroll.h.dist = SCROLL_INCREMENT;

	if (!is_subdevice) {
		if (libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_POINTER))
			driver_data->capabilities |= CAP_POINTER;
		if (libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_KEYBOARD))
			driver_data->capabilities |= CAP_KEYBOARD;
		if (libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_TOUCH))
			driver_data->capabilities |= CAP_TOUCH;
		if (libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_TABLET_TOOL))
			driver_data->capabilities |= CAP_TABLET;
		if (libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_TABLET_PAD))
			driver_data->capabilities |= CAP_TABLET_PAD;
	} else {

		driver_data->capabilities = caps_from_options(pInfo);

		if (driver_data->capabilities & CAP_TABLET_TOOL)
			claim_tablet_tool(pInfo);
	}

	/* Disable acceleration in the server, libinput does it for us */
	pInfo->options = xf86ReplaceIntOption(pInfo->options, "AccelerationProfile", -1);
	pInfo->options = xf86ReplaceStrOption(pInfo->options, "AccelerationScheme", "none");

	xf86libinput_parse_options(pInfo, driver_data, device);

	/* Device is both keyboard and pointer. Drop the keyboard cap from
	 * this device, create a separate device instead */
	if (!is_subdevice &&
	    driver_data->capabilities & CAP_KEYBOARD &&
	    driver_data->capabilities & (CAP_POINTER|CAP_TOUCH)) {
		driver_data->capabilities &= ~CAP_KEYBOARD;
		xf86libinput_create_subdevice(pInfo,
					      CAP_KEYBOARD,
					      NULL);
	}

	pInfo->type_name = xf86libinput_get_type_name(device, driver_data);

	return Success;
fail:
	if (driver_data) {
		if (driver_data->valuators)
			valuator_mask_free(&driver_data->valuators);
		if (driver_data->valuators_unaccelerated)
			valuator_mask_free(&driver_data->valuators_unaccelerated);
	}
	free(path);
	if (shared_device)
		xf86libinput_shared_unref(shared_device);
	free(driver_data);
	if (libinput)
		driver_context.libinput = libinput_unref(libinput);
	return BadValue;
}

static void
xf86libinput_uninit(InputDriverPtr drv,
		    InputInfoPtr pInfo,
		    int flags)
{
	struct xf86libinput *driver_data = pInfo->private;
	if (driver_data) {
		driver_context.libinput = libinput_unref(driver_context.libinput);
		valuator_mask_free(&driver_data->valuators);
		valuator_mask_free(&driver_data->valuators_unaccelerated);
		free(driver_data->path);
		free(driver_data);
		pInfo->private = NULL;
	}
	xf86DeleteInput(pInfo, flags);
}

InputDriverRec xf86libinput_driver = {
	.driverVersion	= 1,
	.driverName	= "libinput",
	.PreInit	= xf86libinput_pre_init,
	.UnInit		= xf86libinput_uninit,
	.module		= NULL,
	.default_options= NULL,
	.capabilities	= XI86_DRV_CAP_SERVER_FD
};

static XF86ModuleVersionInfo xf86libinput_version_info = {
	"libinput",
	MODULEVENDORSTRING,
	MODINFOSTRING1,
	MODINFOSTRING2,
	XORG_VERSION_CURRENT,
	PACKAGE_VERSION_MAJOR, PACKAGE_VERSION_MINOR, PACKAGE_VERSION_PATCHLEVEL,
	ABI_CLASS_XINPUT,
	ABI_XINPUT_VERSION,
	MOD_CLASS_XINPUT,
	{0, 0, 0, 0}
};

static pointer
xf86libinput_setup_proc(pointer module, pointer options, int *errmaj, int *errmin)
{
	xf86AddInputDriver(&xf86libinput_driver, module, 0);
	return module;
}

_X_EXPORT XF86ModuleData libinputModuleData = {
	.vers		= &xf86libinput_version_info,
	.setup		= &xf86libinput_setup_proc,
	.teardown	= NULL
};

/* Property support */

/* libinput-specific properties */
static Atom prop_tap;
static Atom prop_tap_default;
static Atom prop_tap_drag;
static Atom prop_tap_drag_default;
static Atom prop_tap_drag_lock;
static Atom prop_tap_drag_lock_default;
static Atom prop_tap_buttonmap;
static Atom prop_tap_buttonmap_default;
static Atom prop_calibration;
static Atom prop_calibration_default;
static Atom prop_accel;
static Atom prop_accel_default;
static Atom prop_accel_profile_enabled;
static Atom prop_accel_profile_default;
static Atom prop_accel_profiles_available;
static Atom prop_natural_scroll;
static Atom prop_natural_scroll_default;
static Atom prop_sendevents_available;
static Atom prop_sendevents_enabled;
static Atom prop_sendevents_default;
static Atom prop_left_handed;
static Atom prop_left_handed_default;
static Atom prop_scroll_methods_available;
static Atom prop_scroll_method_enabled;
static Atom prop_scroll_method_default;
static Atom prop_scroll_button;
static Atom prop_scroll_button_default;
static Atom prop_scroll_buttonlock;
static Atom prop_scroll_buttonlock_default;
static Atom prop_scroll_pixel_distance;
static Atom prop_scroll_pixel_distance_default;
static Atom prop_click_methods_available;
static Atom prop_click_method_enabled;
static Atom prop_click_method_default;
static Atom prop_middle_emulation;
static Atom prop_middle_emulation_default;
static Atom prop_disable_while_typing;
static Atom prop_disable_while_typing_default;
static Atom prop_mode_groups_available;
static Atom prop_mode_groups;
static Atom prop_mode_groups_buttons;
static Atom prop_mode_groups_rings;
static Atom prop_mode_groups_strips;
static Atom prop_rotation_angle;
static Atom prop_rotation_angle_default;

/* driver properties */
static Atom prop_draglock;
static Atom prop_horiz_scroll;
static Atom prop_pressurecurve;
static Atom prop_area_ratio;

/* general properties */
static Atom prop_float;
static Atom prop_device;
static Atom prop_product_id;

struct mode_prop_state {
	int deviceid;
	InputInfoPtr pInfo;

	struct libinput_tablet_pad_mode_group *group;
	unsigned int mode;
	unsigned int idx;
};

static Bool
update_mode_prop_cb(ClientPtr client, pointer closure)
{
	struct mode_prop_state *state = closure;
	InputInfoPtr pInfo = state->pInfo, tmp;
	struct xf86libinput *driver_data = pInfo->private;
	BOOL found = FALSE;
	XIPropertyValuePtr val;
	int rc;
	unsigned char groups[4] = {0};
	struct libinput_tablet_pad_mode_group *group = state->group;
	unsigned int mode = state->mode;
	unsigned int idx = state->idx;

	if (idx >= ARRAY_SIZE(groups))
		goto out;

	/* The device may have gotten removed before the WorkProc was
	 * scheduled. X reuses deviceids, but if the pointer value and
	 * device ID are what we had before, we're good */
	nt_list_for_each_entry(tmp, xf86FirstLocalDevice(), next) {
		if (tmp->dev->id == state->deviceid && tmp == pInfo) {
			found = TRUE;
			break;
		}
	}
	if (!found)
		goto out;

	rc = XIGetDeviceProperty(pInfo->dev,
				 prop_mode_groups,
				 &val);
	if (rc != Success ||
	    val->format != 8 ||
	    val->size <= 0)
		goto out;

	memcpy(groups, (unsigned char*)val->data, val->size);

	if (groups[idx] == mode)
		goto out;

	groups[idx] = mode;

	driver_data->allow_mode_group_updates = true;
	XIChangeDeviceProperty(pInfo->dev,
			       prop_mode_groups,
			       XA_INTEGER, 8,
			       PropModeReplace,
			       val->size,
			       groups,
			       TRUE);
	driver_data->allow_mode_group_updates = false;

out:
	libinput_tablet_pad_mode_group_unref(group);
	free(state);
	return TRUE;
}

static inline void
update_mode_prop(InputInfoPtr pInfo,
		 struct libinput_event_tablet_pad *event)
{
	struct libinput_tablet_pad_mode_group *group;
	struct mode_prop_state *state;

	state = calloc(1, sizeof(*state));
	if (!state)
		return;

	state->deviceid = pInfo->dev->id;
	state->pInfo = pInfo;

	group = libinput_event_tablet_pad_get_mode_group(event);

	state->group = libinput_tablet_pad_mode_group_ref(group);
	state->mode = libinput_event_tablet_pad_get_mode(event);
	state->idx = libinput_tablet_pad_mode_group_get_index(group);

	/* Schedule a WorkProc so we don't update from within the input
	   thread */
	QueueWorkProc(update_mode_prop_cb, serverClient, state);
}

static inline BOOL
xf86libinput_check_device(DeviceIntPtr dev,
			   Atom atom)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;

	if (device == NULL) {
		BUG_WARN(dev->public.on);
		xf86IDrvMsg(pInfo, X_INFO,
			    "SetProperty on %u called but device is disabled.\n"
			    "This driver cannot change properties on a disabled device\n",
			    atom);
		return FALSE;
	}

	return TRUE;
}

static inline int
LibinputSetPropertyTap(DeviceIntPtr dev,
                       Atom atom,
                       XIPropertyValuePtr val,
                       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;
	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_tap_get_finger_count(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.tapping = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyTapDrag(DeviceIntPtr dev,
			   Atom atom,
			   XIPropertyValuePtr val,
			   BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;
	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_tap_get_finger_count(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.tap_drag = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyTapDragLock(DeviceIntPtr dev,
			       Atom atom,
			       XIPropertyValuePtr val,
			       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;
	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_tap_get_finger_count(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.tap_drag_lock = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyTapButtonmap(DeviceIntPtr dev,
				Atom atom,
				XIPropertyValuePtr val,
				BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	BOOL* data;
	enum libinput_config_tap_button_map map;

	if (val->format != 8 || val->size != 2 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (checkonly) {
	    if ((data[0] && data[1]) || (!data[0] && !data[1]))
		return BadValue;

	    if (!xf86libinput_check_device(dev, atom))
		return BadMatch;
	}

	if (data[0])
		map = LIBINPUT_CONFIG_TAP_MAP_LRM;
	else if (data[1])
		map = LIBINPUT_CONFIG_TAP_MAP_LMR;
	else
		return BadValue;

	if (!checkonly)
		driver_data->options.tap_button_map = map;

	return Success;
}

static inline int
LibinputSetPropertyCalibration(DeviceIntPtr dev,
                               Atom atom,
                               XIPropertyValuePtr val,
			       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	float* data;

	if (val->format != 32 || val->size != 9 || val->type != prop_float)
		return BadMatch;

	data = (float*)val->data;

	if (checkonly) {
		if (data[6] != 0.0 ||
		    data[7] != 0.0 ||
		    data[8] != 1.0)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (!libinput_device_config_calibration_has_matrix(device))
			return BadMatch;
	} else {
		memcpy(driver_data->options.matrix,
		       data,
		       sizeof(driver_data->options.matrix));
	}

	return Success;
}

static inline int
LibinputSetPropertyAccel(DeviceIntPtr dev,
			 Atom atom,
			 XIPropertyValuePtr val,
			 BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	float* data;

	if (val->format != 32 || val->size != 1 || val->type != prop_float)
		return BadMatch;

	data = (float*)val->data;

	if (checkonly) {
		if (*data < -1.0 || *data > 1.0)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_accel_is_available(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.speed = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyAccelProfile(DeviceIntPtr dev,
				Atom atom,
				XIPropertyValuePtr val,
				BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;
	uint32_t profiles = 0;

	if (val->format != 8 || val->size != 2 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (data[0])
		profiles |= LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE;
	if (data[1])
		profiles |= LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT;

	if (checkonly) {
		uint32_t supported;

		if (__builtin_popcount(profiles) > 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_config_accel_get_profiles(device);
		if (profiles && (profiles & supported) == 0)
			return BadValue;
	} else {
		driver_data->options.accel_profile = profiles;
	}

	return Success;
}

static inline int
LibinputSetPropertyNaturalScroll(DeviceIntPtr dev,
                                 Atom atom,
                                 XIPropertyValuePtr val,
                                 BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_scroll_has_natural_scroll(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.natural_scrolling = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertySendEvents(DeviceIntPtr dev,
			      Atom atom,
			      XIPropertyValuePtr val,
			      BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;
	uint32_t modes = 0;

	if (val->format != 8 || val->size != 2 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (data[0])
		modes |= LIBINPUT_CONFIG_SEND_EVENTS_DISABLED;
	if (data[1])
		modes |= LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE;

	if (checkonly) {
		uint32_t supported;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_config_send_events_get_modes(device);
		if ((modes | supported) != supported)
			return BadValue;

	} else {
		driver_data->options.sendevents = modes;
	}

	return Success;
}

static inline int
LibinputSetPropertyLeftHanded(DeviceIntPtr dev,
			      Atom atom,
			      XIPropertyValuePtr val,
			      BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (checkonly) {
		int supported;
		int left_handed = *data;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_config_left_handed_is_available(device);
		if (!supported && left_handed)
			return BadValue;
	} else {
		struct xf86libinput *other;

		driver_data->options.left_handed = *data;

		xorg_list_for_each_entry(other,
					 &driver_data->shared_device->device_list,
					 shared_device_link) {
			DeviceIntPtr other_device = other->pInfo->dev;

			if (other->options.left_handed == *data)
				continue;

			XIChangeDeviceProperty(other_device,
					       atom,
					       val->type,
					       val->format,
					       PropModeReplace,
					       val->size,
					       val->data,
					       TRUE);
		}

	}

	return Success;
}

static inline int
LibinputSetPropertyScrollMethods(DeviceIntPtr dev,
				 Atom atom,
				 XIPropertyValuePtr val,
				 BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;
	uint32_t modes = 0;

	if (val->format != 8 || val->size != 3 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (data[0])
		modes |= LIBINPUT_CONFIG_SCROLL_2FG;
	if (data[1])
		modes |= LIBINPUT_CONFIG_SCROLL_EDGE;
	if (data[2])
		modes |= LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN;

	if (checkonly) {
		uint32_t supported;

		if (__builtin_popcount(modes) > 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_config_scroll_get_methods(device);
		if (modes && (modes & supported) == 0)
			return BadValue;
	} else {
		driver_data->options.scroll_method = modes;
	}

	return Success;
}

static inline int
LibinputSetPropertyScrollButton(DeviceIntPtr dev,
				Atom atom,
				XIPropertyValuePtr val,
				BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	CARD32* data;

	if (val->format != 32 || val->size != 1 || val->type != XA_CARDINAL)
		return BadMatch;

	data = (CARD32*)val->data;

	if (checkonly) {
		uint32_t button = *data;
		uint32_t supported;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_pointer_has_button(device,
							       btn_xorg2linux(button));
		if (button && !supported)
			return BadValue;
	} else {
		driver_data->options.scroll_button = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyScrollButtonLock(DeviceIntPtr dev,
				    Atom atom,
				    XIPropertyValuePtr val,
				    BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	BOOL enabled;

	if (val->format != 8 || val->type != XA_INTEGER || val->size != 1)
		return BadMatch;

	enabled = *(BOOL*)val->data;
	if (checkonly) {
		if (enabled != 0 && enabled != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;
	} else {
		driver_data->options.scroll_buttonlock = enabled;
	}

	return Success;
}

static inline int
LibinputSetPropertyClickMethod(DeviceIntPtr dev,
			       Atom atom,
			       XIPropertyValuePtr val,
			       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;
	uint32_t modes = 0;

	if (val->format != 8 || val->size != 2 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;

	if (data[0])
		modes |= LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS;
	if (data[1])
		modes |= LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER;

	if (checkonly) {
		uint32_t supported;

		if (__builtin_popcount(modes) > 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		supported = libinput_device_config_click_get_methods(device);
		if (modes && (modes & supported) == 0)
			return BadValue;
	} else {
		driver_data->options.click_method = modes;
	}

	return Success;
}

static inline int
LibinputSetPropertyMiddleEmulation(DeviceIntPtr dev,
				   Atom atom,
				   XIPropertyValuePtr val,
				   BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;
	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (!libinput_device_config_middle_emulation_is_available(device))
			return BadMatch;
	} else {
		driver_data->options.middle_emulation = *data;
	}

	return Success;
}

static inline int
LibinputSetPropertyDisableWhileTyping(DeviceIntPtr dev,
				      Atom atom,
				      XIPropertyValuePtr val,
				      BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	BOOL* data;

	if (val->format != 8 || val->size != 1 || val->type != XA_INTEGER)
		return BadMatch;

	data = (BOOL*)val->data;
	if (checkonly) {
		if (*data != 0 && *data != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (!libinput_device_config_dwt_is_available(device))
			return BadMatch;
	} else {
		driver_data->options.disable_while_typing = *data;
	}

	return Success;
}

static inline int
prop_draglock_set_meta(struct xf86libinput *driver_data,
		       const BYTE *values,
		       int len,
		       BOOL checkonly)
{
	struct draglock *dl,
			dummy; /* for checkonly */
	int meta;

	if (len > 1)
		return BadImplementation; /* should not happen */

	dl = (checkonly) ? &dummy : &driver_data->draglock;
	meta = len > 0 ? values[0] : 0;

	return draglock_set_meta(dl, meta) == 0 ? Success: BadValue;
}

static inline int
prop_draglock_set_pairs(struct xf86libinput *driver_data,
			const BYTE* pairs,
			int len,
			BOOL checkonly)
{
	struct draglock *dl,
			dummy; /* for checkonly */
	int data[MAX_BUTTONS + 1] = {0};
	int i;
	int highest = 0;

	if (len >= ARRAY_SIZE(data))
		return BadMatch;

	if (len < 2 || len % 2)
		return BadImplementation; /* should not happen */

	dl = (checkonly) ? &dummy : &driver_data->draglock;

	for (i = 0; i < len; i += 2) {
		if (pairs[i] > MAX_BUTTONS)
			return BadValue;

		data[pairs[i]] = pairs[i+1];
		highest = max(highest, pairs[i]);
	}

	return draglock_set_pairs(dl, data, highest + 1) == 0 ? Success : BadValue;
}

static inline int
LibinputSetPropertyDragLockButtons(DeviceIntPtr dev,
				   Atom atom,
				   XIPropertyValuePtr val,
				   BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;

	if (val->format != 8 || val->type != XA_INTEGER)
		return BadMatch;

	/* either a single value, or pairs of values */
	if (val->size > 1 && val->size % 2)
		return BadMatch;

	if (!xf86libinput_check_device(dev, atom))
		return BadMatch;

	if (val->size <= 1)
		return prop_draglock_set_meta(driver_data,
					      (BYTE*)val->data,
					      val->size, checkonly);
	else
		return prop_draglock_set_pairs(driver_data,
					       (BYTE*)val->data,
					       val->size, checkonly);
}

static inline int
LibinputSetPropertyHorizScroll(DeviceIntPtr dev,
			       Atom atom,
			       XIPropertyValuePtr val,
			       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	BOOL enabled;

	if (val->format != 8 || val->type != XA_INTEGER || val->size != 1)
		return BadMatch;

	enabled = *(BOOL*)val->data;
	if (checkonly) {
		if (enabled != 0 && enabled != 1)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;
	} else {
		driver_data->options.horiz_scrolling_enabled = enabled;
	}

	return Success;
}

static inline int
LibinputSetPropertyScrollPixelDistance(DeviceIntPtr dev,
				       Atom atom,
				       XIPropertyValuePtr val,
				       BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	uint32_t dist;

	if (val->format != 32 || val->type != XA_CARDINAL || val->size != 1)
		return BadMatch;

	dist = *(BOOL*)val->data;
	if (checkonly) {
		if (dist < TOUCHPAD_SCROLL_DIST_MIN ||
		    dist > TOUCHPAD_SCROLL_DIST_MAX)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;
	} else {
		driver_data->options.scroll_pixel_distance = dist;
	}

	return Success;
}

static inline int
LibinputSetPropertyRotationAngle(DeviceIntPtr dev,
				 Atom atom,
				 XIPropertyValuePtr val,
				 BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	float *angle;

	if (val->format != 32 || val->size != 1 || val->type != prop_float)
		return BadMatch;

	angle = (float*)val->data;

	if (checkonly) {
		if (*angle < 0.0 || *angle >= 360.0)
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (libinput_device_config_rotation_is_available(device) == 0)
			return BadMatch;
	} else {
		driver_data->options.rotation_angle = *angle;
	}

	return Success;
}

static inline int
LibinputSetPropertyPressureCurve(DeviceIntPtr dev,
				 Atom atom,
				 XIPropertyValuePtr val,
				 BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	float *vals;
	struct bezier_control_point controls[4];

	if (val->format != 32 || val->size != 8 || val->type != prop_float)
		return BadMatch;

	vals = val->data;
	controls[0].x = vals[0];
	controls[0].y = vals[1];
	controls[1].x = vals[2];
	controls[1].y = vals[3];
	controls[2].x = vals[4];
	controls[2].y = vals[5];
	controls[3].x = vals[6];
	controls[3].y = vals[7];

	if (checkonly) {
		int test_bezier[64];

		for (int i = 0; i < val->size; i++) {
			if (vals[i] < 0.0 || vals[i] > 1.0)
				return BadValue;
		}

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;

		if (!cubic_bezier(controls, test_bezier, ARRAY_SIZE(test_bezier)))
			return BadValue;
	} else {
		xf86libinput_set_pressurecurve(driver_data, controls);
		memcpy(driver_data->options.pressurecurve, controls,
		       sizeof(controls));
	}

	return Success;
}

static inline int
LibinputSetPropertyAreaRatio(DeviceIntPtr dev,
			     Atom atom,
			     XIPropertyValuePtr val,
			     BOOL checkonly)
{
	InputInfoPtr pInfo = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	uint32_t *vals;
	struct ratio area = { 0, 0 };

	if (val->format != 32 || val->size != 2 || val->type != XA_CARDINAL)
		return BadMatch;

	vals = val->data;
	area.x = vals[0];
	area.y = vals[1];

	if (checkonly) {
		if (area.x < 0 || area.y < 0)
			return BadValue;

		if ((area.x != 0 && area.y == 0) ||
		    (area.x == 0 && area.y != 0))
			return BadValue;

		if (!xf86libinput_check_device(dev, atom))
			return BadMatch;
	} else {
		struct xf86libinput *other;

		xf86libinput_set_area_ratio(driver_data, &area);

		xorg_list_for_each_entry(other,
					 &driver_data->shared_device->device_list,
					 shared_device_link) {
			DeviceIntPtr other_device = other->pInfo->dev;

			if (other->options.area.x == area.x &&
			    other->options.area.y == area.y)
				continue;

			XIChangeDeviceProperty(other_device,
					       atom,
					       val->type,
					       val->format,
					       PropModeReplace,
					       val->size,
					       val->data,
					       TRUE);
		}
	}

	return Success;
}

static int
LibinputSetProperty(DeviceIntPtr dev, Atom atom, XIPropertyValuePtr val,
                 BOOL checkonly)
{
	int rc;

	if (atom == prop_tap)
		rc = LibinputSetPropertyTap(dev, atom, val, checkonly);
	else if (atom == prop_tap_drag)
		rc = LibinputSetPropertyTapDrag(dev, atom, val, checkonly);
	else if (atom == prop_tap_drag_lock)
		rc = LibinputSetPropertyTapDragLock(dev, atom, val, checkonly);
	else if (atom == prop_tap_buttonmap)
		rc = LibinputSetPropertyTapButtonmap(dev, atom, val, checkonly);
	else if (atom == prop_calibration)
		rc = LibinputSetPropertyCalibration(dev, atom, val,
						    checkonly);
	else if (atom == prop_accel)
		rc = LibinputSetPropertyAccel(dev, atom, val, checkonly);
	else if (atom == prop_accel_profile_enabled)
		rc = LibinputSetPropertyAccelProfile(dev, atom, val, checkonly);
	else if (atom == prop_natural_scroll)
		rc = LibinputSetPropertyNaturalScroll(dev, atom, val, checkonly);
	else if (atom == prop_sendevents_enabled)
		rc = LibinputSetPropertySendEvents(dev, atom, val, checkonly);
	else if (atom == prop_left_handed)
		rc = LibinputSetPropertyLeftHanded(dev, atom, val, checkonly);
	else if (atom == prop_scroll_method_enabled)
		rc = LibinputSetPropertyScrollMethods(dev, atom, val, checkonly);
	else if (atom == prop_scroll_button)
		rc = LibinputSetPropertyScrollButton(dev, atom, val, checkonly);
	else if (atom == prop_scroll_buttonlock)
		rc = LibinputSetPropertyScrollButtonLock(dev, atom, val, checkonly);
	else if (atom == prop_click_method_enabled)
		rc = LibinputSetPropertyClickMethod(dev, atom, val, checkonly);
	else if (atom == prop_middle_emulation)
		rc = LibinputSetPropertyMiddleEmulation(dev, atom, val, checkonly);
	else if (atom == prop_disable_while_typing)
		rc = LibinputSetPropertyDisableWhileTyping(dev, atom, val, checkonly);
	else if (atom == prop_draglock)
		rc = LibinputSetPropertyDragLockButtons(dev, atom, val, checkonly);
	else if (atom == prop_horiz_scroll)
		rc = LibinputSetPropertyHorizScroll(dev, atom, val, checkonly);
	else if (atom == prop_scroll_pixel_distance)
		rc = LibinputSetPropertyScrollPixelDistance(dev, atom, val, checkonly);
	else if (atom == prop_mode_groups) {
		InputInfoPtr pInfo = dev->public.devicePrivate;
		struct xf86libinput *driver_data = pInfo->private;

		if (driver_data->allow_mode_group_updates)
			return Success;
		else
			return BadAccess;
	}
	else if (atom == prop_rotation_angle)
		rc = LibinputSetPropertyRotationAngle(dev, atom, val, checkonly);
	else if (atom == prop_pressurecurve)
		rc = LibinputSetPropertyPressureCurve(dev, atom, val, checkonly);
	else if (atom == prop_area_ratio)
		rc = LibinputSetPropertyAreaRatio(dev, atom, val, checkonly);
	else if (atom == prop_device || atom == prop_product_id ||
		 atom == prop_tap_default ||
		 atom == prop_tap_drag_default ||
		 atom == prop_tap_drag_lock_default ||
		 atom == prop_tap_buttonmap_default ||
		 atom == prop_calibration_default ||
		 atom == prop_accel_default ||
		 atom == prop_accel_profile_default ||
		 atom == prop_natural_scroll_default ||
		 atom == prop_sendevents_default ||
		 atom == prop_sendevents_available ||
		 atom == prop_left_handed_default ||
		 atom == prop_scroll_method_default ||
		 atom == prop_scroll_methods_available ||
		 atom == prop_scroll_button_default ||
		 atom == prop_scroll_buttonlock_default ||
		 atom == prop_scroll_pixel_distance_default ||
		 atom == prop_click_method_default ||
		 atom == prop_click_methods_available ||
		 atom == prop_middle_emulation_default ||
		 atom == prop_disable_while_typing_default ||
		 atom == prop_mode_groups_available ||
		 atom == prop_mode_groups_buttons ||
		 atom == prop_mode_groups_rings ||
		 atom == prop_mode_groups_strips ||
		 atom == prop_rotation_angle_default)
		return BadAccess; /* read-only */
	else
		return Success;

	if (!checkonly && rc == Success)
		LibinputApplyConfig(dev);

	return rc;
}

static Atom
LibinputMakeProperty(DeviceIntPtr dev,
		     const char *prop_name,
		     Atom type,
		     int format,
		     int len,
		     void *data)
{
	int rc;
	Atom prop = MakeAtom(prop_name, strlen(prop_name), TRUE);

	rc = XIChangeDeviceProperty(dev, prop, type, format,
				    PropModeReplace,
				    len, data, FALSE);
	if (rc != Success)
		return None;

	XISetDevicePropertyDeletable(dev, prop, FALSE);

	return prop;
}

static void
LibinputInitTapProperty(DeviceIntPtr dev,
			struct xf86libinput *driver_data,
			struct libinput_device *device)
{
	BOOL tap = driver_data->options.tapping;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return;

	prop_tap = LibinputMakeProperty(dev,
					LIBINPUT_PROP_TAP,
					XA_INTEGER,
					8,
					1,
					&tap);
	if (!prop_tap)
		return;

	tap = libinput_device_config_tap_get_default_enabled(device);
	prop_tap_default = LibinputMakeProperty(dev,
						LIBINPUT_PROP_TAP_DEFAULT,
						XA_INTEGER, 8,
						1, &tap);
}

static void
LibinputInitTapDragProperty(DeviceIntPtr dev,
			    struct xf86libinput *driver_data,
			    struct libinput_device *device)
{
	BOOL drag = driver_data->options.tap_drag;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return;

	prop_tap_drag = LibinputMakeProperty(dev,
					     LIBINPUT_PROP_TAP_DRAG,
					     XA_INTEGER, 8,
					     1, &drag);
	if (!prop_tap_drag)
		return;

	drag = libinput_device_config_tap_get_default_drag_enabled(device);
	prop_tap_drag_default = LibinputMakeProperty(dev,
						     LIBINPUT_PROP_TAP_DRAG_DEFAULT,
						     XA_INTEGER, 8,
						     1, &drag);
}

static void
LibinputInitTapDragLockProperty(DeviceIntPtr dev,
				struct xf86libinput *driver_data,
				struct libinput_device *device)
{
	BOOL drag_lock = driver_data->options.tap_drag_lock;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return;

	prop_tap_drag_lock = LibinputMakeProperty(dev,
						  LIBINPUT_PROP_TAP_DRAG_LOCK,
						  XA_INTEGER, 8,
						  1, &drag_lock);
	if (!prop_tap_drag_lock)
		return;

	drag_lock = libinput_device_config_tap_get_default_drag_lock_enabled(device);
	prop_tap_drag_lock_default = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_TAP_DRAG_LOCK_DEFAULT,
							  XA_INTEGER, 8,
							  1, &drag_lock);
}

static void
LibinputInitTapButtonmapProperty(DeviceIntPtr dev,
				 struct xf86libinput *driver_data,
				 struct libinput_device *device)
{
	enum libinput_config_tap_button_map map;
	BOOL data[2] = {0};

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	map = driver_data->options.tap_button_map;

	if (libinput_device_config_tap_get_finger_count(device) == 0)
		return;

	switch (map) {
	case LIBINPUT_CONFIG_TAP_MAP_LRM:
		data[0] = 1;
		break;
	case LIBINPUT_CONFIG_TAP_MAP_LMR:
		data[1] = 1;
		break;
	default:
		break;
	}

	prop_tap_buttonmap = LibinputMakeProperty(dev,
						  LIBINPUT_PROP_TAP_BUTTONMAP,
						  XA_INTEGER, 8,
						  2, data);
	if (!prop_tap_buttonmap)
		return;

	map = libinput_device_config_tap_get_default_button_map(device);
	memset(data, 0, sizeof(data));

	switch (map) {
	case LIBINPUT_CONFIG_TAP_MAP_LRM:
		data[0] = 1;
		break;
	case LIBINPUT_CONFIG_TAP_MAP_LMR:
		data[1] = 1;
		break;
	default:
		break;
	}

	prop_tap_buttonmap_default = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_TAP_BUTTONMAP_DEFAULT,
							  XA_INTEGER, 8,
							  2, data);
}

static void
LibinputInitCalibrationProperty(DeviceIntPtr dev,
				struct xf86libinput *driver_data,
				struct libinput_device *device)
{
	float calibration[9];

	if (!subdevice_has_capabilities(dev, CAP_POINTER|CAP_TOUCH|CAP_TABLET))
		return;

	if (!libinput_device_config_calibration_has_matrix(device))
		return;

	/* We use a 9-element matrix just to be closer to the X server's
	   transformation matrix which also has the full matrix */

	libinput_device_config_calibration_get_matrix(device, calibration);
	calibration[6] = 0.0;
	calibration[7] = 0.0;
	calibration[8] = 1.0;

	prop_calibration = LibinputMakeProperty(dev,
						LIBINPUT_PROP_CALIBRATION,
						prop_float, 32,
						9, calibration);
	if (!prop_calibration)
		return;

	libinput_device_config_calibration_get_default_matrix(device,
							      calibration);

	prop_calibration_default = LibinputMakeProperty(dev,
							LIBINPUT_PROP_CALIBRATION_DEFAULT,
							prop_float, 32,
							9, calibration);
}

static void
LibinputInitAccelProperty(DeviceIntPtr dev,
			  struct xf86libinput *driver_data,
			  struct libinput_device *device)
{
	float speed = driver_data->options.speed;
	uint32_t profile_mask;
	enum libinput_config_accel_profile profile;
	BOOL profiles[2] = {FALSE};

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (!libinput_device_config_accel_is_available(device) ||
	    driver_data->capabilities & CAP_TABLET)
		return;

	prop_accel = LibinputMakeProperty(dev,
					  LIBINPUT_PROP_ACCEL,
					  prop_float, 32,
					  1, &speed);
	if (!prop_accel)
		return;

	speed = libinput_device_config_accel_get_default_speed(device);
	prop_accel_default = LibinputMakeProperty(dev,
						  LIBINPUT_PROP_ACCEL_DEFAULT,
						  prop_float, 32,
						  1, &speed);

	profile_mask = libinput_device_config_accel_get_profiles(device);
	if (profile_mask == LIBINPUT_CONFIG_ACCEL_PROFILE_NONE)
		return;

	if (profile_mask & LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE)
		profiles[0] = TRUE;
	if (profile_mask & LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE)
		profiles[1] = TRUE;

	prop_accel_profiles_available = LibinputMakeProperty(dev,
							     LIBINPUT_PROP_ACCEL_PROFILES_AVAILABLE,
							     XA_INTEGER, 8,
							     ARRAY_SIZE(profiles),
							     profiles);
	if (!prop_accel_profiles_available)
		return;

	memset(profiles, 0, sizeof(profiles));

	profile = libinput_device_config_accel_get_profile(device);
	switch(profile) {
	case LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE:
		profiles[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT:
		profiles[1] = TRUE;
		break;
	default:
		break;
	}

	prop_accel_profile_enabled = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_ACCEL_PROFILE_ENABLED,
							  XA_INTEGER, 8,
							  ARRAY_SIZE(profiles),
							  profiles);
	if (!prop_accel_profile_enabled)
		return;

	memset(profiles, 0, sizeof(profiles));

	profile = libinput_device_config_accel_get_default_profile(device);
	switch(profile) {
	case LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE:
		profiles[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT:
		profiles[1] = TRUE;
		break;
	default:
		break;
	}

	prop_accel_profile_default = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_ACCEL_PROFILE_ENABLED_DEFAULT,
							  XA_INTEGER, 8,
							  ARRAY_SIZE(profiles),
							  profiles);
	if (!prop_accel_profile_default)
		return;

}

static void
LibinputInitNaturalScrollProperty(DeviceIntPtr dev,
				  struct xf86libinput *driver_data,
				  struct libinput_device *device)
{
	BOOL natural_scroll = driver_data->options.natural_scrolling;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (!libinput_device_config_scroll_has_natural_scroll(device))
		return;

	prop_natural_scroll = LibinputMakeProperty(dev,
						   LIBINPUT_PROP_NATURAL_SCROLL,
						   XA_INTEGER, 8,
						   1, &natural_scroll);
	if (!prop_natural_scroll)
		return;

	natural_scroll = libinput_device_config_scroll_get_default_natural_scroll_enabled(device);
	prop_natural_scroll_default = LibinputMakeProperty(dev,
							   LIBINPUT_PROP_NATURAL_SCROLL_DEFAULT,
							   XA_INTEGER, 8,
							   1, &natural_scroll);
}

static void
LibinputInitSendEventsProperty(DeviceIntPtr dev,
			       struct xf86libinput *driver_data,
			       struct libinput_device *device)
{
	uint32_t sendevent_modes;
	uint32_t sendevents;
	BOOL modes[2] = {FALSE};

	sendevent_modes = libinput_device_config_send_events_get_modes(device);
	if (sendevent_modes == LIBINPUT_CONFIG_SEND_EVENTS_ENABLED)
		return;

	if (sendevent_modes & LIBINPUT_CONFIG_SEND_EVENTS_DISABLED)
		modes[0] = TRUE;
	if (sendevent_modes & LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE)
		modes[1] = TRUE;

	prop_sendevents_available = LibinputMakeProperty(dev,
							 LIBINPUT_PROP_SENDEVENTS_AVAILABLE,
							 XA_INTEGER, 8,
							 2, modes);
	if (!prop_sendevents_available)
		return;

	memset(modes, 0, sizeof(modes));
	sendevents = driver_data->options.sendevents;

	switch(sendevents) {
	case LIBINPUT_CONFIG_SEND_EVENTS_DISABLED:
		modes[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE:
		modes[1] = TRUE;
		break;
	}

	prop_sendevents_enabled = LibinputMakeProperty(dev,
						       LIBINPUT_PROP_SENDEVENTS_ENABLED,
						       XA_INTEGER, 8,
						       2, modes);

	if (!prop_sendevents_enabled)
		return;

	memset(modes, 0, sizeof(modes));
	sendevent_modes = libinput_device_config_send_events_get_default_mode(device);
	if (sendevent_modes & LIBINPUT_CONFIG_SEND_EVENTS_DISABLED)
		modes[0] = TRUE;
	if (sendevent_modes & LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE)
		modes[1] = TRUE;

	prop_sendevents_default = LibinputMakeProperty(dev,
						       LIBINPUT_PROP_SENDEVENTS_ENABLED_DEFAULT,
						       XA_INTEGER, 8,
						       2, modes);
}

static void
LibinputInitLeftHandedProperty(DeviceIntPtr dev,
			       struct xf86libinput *driver_data,
			       struct libinput_device *device)
{
	BOOL left_handed = driver_data->options.left_handed;

	if (!subdevice_has_capabilities(dev, CAP_POINTER|CAP_TABLET))
		return;

	if (!libinput_device_config_left_handed_is_available(device) ||
	    driver_data->capabilities & CAP_TABLET)
		return;

	prop_left_handed = LibinputMakeProperty(dev,
						LIBINPUT_PROP_LEFT_HANDED,
						XA_INTEGER, 8,
						1, &left_handed);
	if (!prop_left_handed)
		return;

	left_handed = libinput_device_config_left_handed_get_default(device);
	prop_left_handed_default = LibinputMakeProperty(dev,
							LIBINPUT_PROP_LEFT_HANDED_DEFAULT,
							XA_INTEGER, 8,
							1, &left_handed);
}

static void
LibinputInitScrollMethodsProperty(DeviceIntPtr dev,
				  struct xf86libinput *driver_data,
				  struct libinput_device *device)
{
	uint32_t scroll_methods;
	enum libinput_config_scroll_method method;
	BOOL methods[3] = {FALSE};

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	scroll_methods = libinput_device_config_scroll_get_methods(device);
	if (scroll_methods == LIBINPUT_CONFIG_SCROLL_NO_SCROLL)
		return;

	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_2FG)
		methods[0] = TRUE;
	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_EDGE)
		methods[1] = TRUE;
	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN)
		methods[2] = TRUE;

	prop_scroll_methods_available = LibinputMakeProperty(dev,
							     LIBINPUT_PROP_SCROLL_METHODS_AVAILABLE,
							     XA_INTEGER, 8,
							     ARRAY_SIZE(methods),
							     methods);
	if (!prop_scroll_methods_available)
		return;

	memset(methods, 0, sizeof(methods));

	method = libinput_device_config_scroll_get_method(device);
	switch(method) {
	case LIBINPUT_CONFIG_SCROLL_2FG:
		methods[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_SCROLL_EDGE:
		methods[1] = TRUE;
		break;
	case LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN:
		methods[2] = TRUE;
		break;
	default:
		break;
	}

	prop_scroll_method_enabled = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_SCROLL_METHOD_ENABLED,
							  XA_INTEGER, 8,
							  ARRAY_SIZE(methods),
							  methods);
	if (!prop_scroll_method_enabled)
		return;

	scroll_methods = libinput_device_config_scroll_get_default_method(device);
	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_2FG)
		methods[0] = TRUE;
	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_EDGE)
		methods[1] = TRUE;
	if (scroll_methods & LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN)
		methods[2] = TRUE;

	prop_scroll_method_default = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_SCROLL_METHOD_ENABLED_DEFAULT,
							  XA_INTEGER, 8,
							  ARRAY_SIZE(methods),
							  methods);
	/* Scroll button and scroll button lock */
	if (libinput_device_config_scroll_get_methods(device) &
	    LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN) {
		CARD32 scroll_button = driver_data->options.scroll_button;
		BOOL lock_enabled = driver_data->options.scroll_buttonlock;

		prop_scroll_button = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_SCROLL_BUTTON,
							  XA_CARDINAL, 32,
							  1, &scroll_button);
		if (!prop_scroll_button)
			return;

#if HAVE_LIBINPUT_SCROLL_BUTTON_LOCK
		scroll_button = libinput_device_config_scroll_get_default_button(device);
		scroll_button = btn_linux2xorg(scroll_button);
		prop_scroll_button_default = LibinputMakeProperty(dev,
								  LIBINPUT_PROP_SCROLL_BUTTON_DEFAULT,
								  XA_CARDINAL, 32,
								  1, &scroll_button);
		prop_scroll_buttonlock = LibinputMakeProperty(dev,
							      LIBINPUT_PROP_SCROLL_BUTTON_LOCK,
							      XA_INTEGER, 8,
							      1, &lock_enabled);
		if (!prop_scroll_buttonlock)
			return;

		lock_enabled = libinput_device_config_scroll_get_default_button_lock(device);
		prop_scroll_buttonlock_default = LibinputMakeProperty(dev,
								      LIBINPUT_PROP_SCROLL_BUTTON_LOCK_DEFAULT,
								      XA_INTEGER, 8,
								      1, &lock_enabled);
#endif
	}
}

static void
LibinputInitScrollPixelDistanceProperty(DeviceIntPtr dev,
					struct xf86libinput *driver_data,
					struct libinput_device *device)
{
	CARD32 dist = driver_data->options.scroll_pixel_distance;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (!xf86libinput_want_scroll_distance_option(device))
		return;

	prop_scroll_pixel_distance = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_SCROLL_PIXEL_DISTANCE,
							  XA_CARDINAL, 32,
							  1, &dist);
	if (!prop_scroll_pixel_distance)
		return;

	prop_scroll_pixel_distance_default = LibinputMakeProperty(dev,
								  LIBINPUT_PROP_SCROLL_PIXEL_DISTANCE_DEFAULT,
								  XA_CARDINAL, 32,
								  1, &dist);
}

static void
LibinputInitClickMethodsProperty(DeviceIntPtr dev,
				 struct xf86libinput *driver_data,
				 struct libinput_device *device)
{
	uint32_t click_methods;
	enum libinput_config_click_method method;
	BOOL methods[2] = {FALSE};

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	click_methods = libinput_device_config_click_get_methods(device);
	if (click_methods == LIBINPUT_CONFIG_CLICK_METHOD_NONE)
		return;

	if (click_methods & LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS)
		methods[0] = TRUE;
	if (click_methods & LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER)
		methods[1] = TRUE;

	prop_click_methods_available = LibinputMakeProperty(dev,
							    LIBINPUT_PROP_CLICK_METHODS_AVAILABLE,
							    XA_INTEGER, 8,
							    ARRAY_SIZE(methods),
							    methods);
	if (!prop_click_methods_available)
		return;

	memset(methods, 0, sizeof(methods));

	method = libinput_device_config_click_get_method(device);
	switch(method) {
	case LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS:
		methods[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER:
		methods[1] = TRUE;
		break;
	default:
		break;
	}

	prop_click_method_enabled = LibinputMakeProperty(dev,
							 LIBINPUT_PROP_CLICK_METHOD_ENABLED,
							 XA_INTEGER, 8,
							 ARRAY_SIZE(methods),
							 methods);

	if (!prop_click_method_enabled)
		return;

	memset(methods, 0, sizeof(methods));

	method = libinput_device_config_click_get_default_method(device);
	switch(method) {
	case LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS:
		methods[0] = TRUE;
		break;
	case LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER:
		methods[1] = TRUE;
		break;
	default:
		break;
	}

	prop_click_method_default = LibinputMakeProperty(dev,
							 LIBINPUT_PROP_CLICK_METHOD_ENABLED_DEFAULT,
							 XA_INTEGER, 8,
							 ARRAY_SIZE(methods),
							 methods);
}

static void
LibinputInitMiddleEmulationProperty(DeviceIntPtr dev,
				    struct xf86libinput *driver_data,
				    struct libinput_device *device)
{
	BOOL middle = driver_data->options.middle_emulation;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (!libinput_device_config_middle_emulation_is_available(device))
		return;

	prop_middle_emulation = LibinputMakeProperty(dev,
						     LIBINPUT_PROP_MIDDLE_EMULATION_ENABLED,
						     XA_INTEGER,
						     8,
						     1,
						     &middle);
	if (!prop_middle_emulation)
		return;

	middle = libinput_device_config_middle_emulation_get_default_enabled(device);
	prop_middle_emulation_default = LibinputMakeProperty(dev,
							     LIBINPUT_PROP_MIDDLE_EMULATION_ENABLED_DEFAULT,
							     XA_INTEGER, 8,
							     1, &middle);
}

static void
LibinputInitDisableWhileTypingProperty(DeviceIntPtr dev,
				       struct xf86libinput *driver_data,
				       struct libinput_device *device)
{
	BOOL dwt = driver_data->options.disable_while_typing;

	if (!subdevice_has_capabilities(dev, CAP_POINTER))
		return;

	if (!libinput_device_config_dwt_is_available(device))
		return;

	prop_disable_while_typing = LibinputMakeProperty(dev,
							 LIBINPUT_PROP_DISABLE_WHILE_TYPING,
							 XA_INTEGER,
							 8,
							 1,
							 &dwt);
	if (!prop_disable_while_typing)
		return;

	dwt = libinput_device_config_dwt_get_default_enabled(device);
	prop_disable_while_typing_default = LibinputMakeProperty(dev,
								 LIBINPUT_PROP_DISABLE_WHILE_TYPING_DEFAULT,
								 XA_INTEGER, 8,
								 1, &dwt);
}

static void
LibinputInitModeGroupProperties(DeviceIntPtr dev,
				       struct xf86libinput *driver_data,
				       struct libinput_device *device)
{
	struct libinput_tablet_pad_mode_group *group;
	int ngroups, nmodes, mode;
	int nbuttons, nstrips, nrings;
	unsigned char groups[4] = {0},
		      current[4] = {0},
		      associations[MAX_BUTTONS] = {0};
	int g, b, r, s;

	if (!subdevice_has_capabilities(dev, CAP_TABLET_PAD))
		return;

	if (!libinput_device_has_capability(device, LIBINPUT_DEVICE_CAP_TABLET_PAD))
		return;

	ngroups = libinput_device_tablet_pad_get_num_mode_groups(device);
	if (ngroups <= 0)
		return;

	group = libinput_device_tablet_pad_get_mode_group(device, 0);
	nmodes = libinput_tablet_pad_mode_group_get_num_modes(group);
	if (ngroups == 1 && nmodes == 1)
		return;

	ngroups = min(ngroups, ARRAY_SIZE(groups));
	for (g = 0; g < ngroups; g++) {
		group = libinput_device_tablet_pad_get_mode_group(device, g);
		nmodes = libinput_tablet_pad_mode_group_get_num_modes(group);
		mode = libinput_tablet_pad_mode_group_get_mode(group);

		groups[g] = nmodes;
		current[g] = mode;
	}

	prop_mode_groups_available = LibinputMakeProperty(dev,
							  LIBINPUT_PROP_TABLET_PAD_MODE_GROUPS_AVAILABLE,
							  XA_INTEGER,
							  8,
							  ngroups,
							  groups);
	if (!prop_mode_groups_available)
		return;

	prop_mode_groups = LibinputMakeProperty(dev,
						LIBINPUT_PROP_TABLET_PAD_MODE_GROUPS,
						XA_INTEGER,
						8,
						ngroups,
						current);
	if (!prop_mode_groups)
		return;

	for (b = 0; b < ARRAY_SIZE(associations); b++)
		associations[b] = -1;

	nbuttons = libinput_device_tablet_pad_get_num_buttons(device);
	for (b = 0; b < nbuttons; b++) {
		/* logical buttons exclude scroll wheel buttons */
		int lb = b <= 3 ? b : b + 4;
		associations[lb] = -1;
		for (g = 0; g < ngroups; g++) {
			group = libinput_device_tablet_pad_get_mode_group(device, g);
			if (libinput_tablet_pad_mode_group_has_button(group, b)) {
				associations[lb] = g;
				break;
			}
		}
	}

	prop_mode_groups_buttons = LibinputMakeProperty(dev,
							LIBINPUT_PROP_TABLET_PAD_MODE_GROUP_BUTTONS,
							XA_INTEGER,
							8,
							nbuttons,
							associations);
	if (!prop_mode_groups_buttons)
		return;

	nrings = libinput_device_tablet_pad_get_num_rings(device);
	if (nrings) {
		for (r = 0; r < nrings; r++) {
			associations[r] = -1;
			for (g = 0; g < ngroups; g++) {
				group = libinput_device_tablet_pad_get_mode_group(device, g);
				if (libinput_tablet_pad_mode_group_has_ring(group, r)) {
					associations[r] = g;
					break;
				}
			}
		}

		prop_mode_groups_rings = LibinputMakeProperty(dev,
								LIBINPUT_PROP_TABLET_PAD_MODE_GROUP_RINGS,
								XA_INTEGER,
								8,
								nrings,
								associations);
		if (!prop_mode_groups_rings)
			return;
	}

	nstrips = libinput_device_tablet_pad_get_num_strips(device);
	if (nstrips) {
		for (s = 0; s < nstrips; s++) {
			associations[s] = -1;
			for (g = 0; g < ngroups; g++) {
				group = libinput_device_tablet_pad_get_mode_group(device, g);
				if (libinput_tablet_pad_mode_group_has_strip(group, s)) {
					associations[s] = g;
					break;
				}
			}
		}

		prop_mode_groups_strips = LibinputMakeProperty(dev,
								LIBINPUT_PROP_TABLET_PAD_MODE_GROUP_STRIPS,
								XA_INTEGER,
								8,
								nstrips,
								associations);
		if (!prop_mode_groups_strips)
			return;
	}
}

static void
LibinputInitDragLockProperty(DeviceIntPtr dev,
			     struct xf86libinput *driver_data)
{
	size_t sz;
	int dl_values[MAX_BUTTONS + 1];

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	switch (draglock_get_mode(&driver_data->draglock)) {
	case DRAGLOCK_DISABLED:
		sz = 0; /* will be an empty property */
		break;
	case DRAGLOCK_META:
		dl_values[0] = draglock_get_meta(&driver_data->draglock);
		sz = 1;
		break;
	case DRAGLOCK_PAIRS:
		sz = draglock_get_pairs(&driver_data->draglock,
					dl_values, ARRAY_SIZE(dl_values));
		break;
	default:
		xf86IDrvMsg(dev->public.devicePrivate,
			    X_ERROR,
			    "Invalid drag lock mode\n");
		return;
	}

	prop_draglock = LibinputMakeProperty(dev,
					     LIBINPUT_PROP_DRAG_LOCK_BUTTONS,
					     XA_INTEGER, 8,
					     sz, dl_values);
}

static void
LibinputInitHorizScrollProperty(DeviceIntPtr dev,
				struct xf86libinput *driver_data)
{
	BOOL enabled = driver_data->options.horiz_scrolling_enabled;

	if ((driver_data->capabilities & CAP_POINTER) == 0)
		return;

	prop_horiz_scroll = LibinputMakeProperty(dev,
						 LIBINPUT_PROP_HORIZ_SCROLL_ENABLED,
						 XA_INTEGER, 8,
						 1, &enabled);
}

static void
LibinputInitRotationAngleProperty(DeviceIntPtr dev,
				  struct xf86libinput *driver_data,
				  struct libinput_device *device)
{
	float angle = driver_data->options.rotation_angle;

	if (!libinput_device_config_rotation_is_available(device))
		return;

	prop_rotation_angle = LibinputMakeProperty(dev,
						   LIBINPUT_PROP_ROTATION_ANGLE,
						   prop_float, 32,
						   1, &angle);
	if (!prop_rotation_angle)
		return;

	angle = libinput_device_config_rotation_get_default_angle(device);
	prop_rotation_angle_default = LibinputMakeProperty(dev,
							   LIBINPUT_PROP_ROTATION_ANGLE_DEFAULT,
							   prop_float, 32,
							   1, &angle);

	if (!prop_rotation_angle_default)
		return;
}

static void
LibinputInitPressureCurveProperty(DeviceIntPtr dev,
				  struct xf86libinput *driver_data)
{
	const struct bezier_control_point *curve = driver_data->options.pressurecurve;
	struct libinput_tablet_tool *tool = driver_data->tablet_tool;
	float data[8];

	if ((driver_data->capabilities & CAP_TABLET_TOOL) == 0)
		return;

	if (!tool || !libinput_tablet_tool_has_pressure(tool))
		return;

	data[0] = curve[0].x;
	data[1] = curve[0].y;
	data[2] = curve[1].x;
	data[3] = curve[1].y;
	data[4] = curve[2].x;
	data[5] = curve[2].y;
	data[6] = curve[3].x;
	data[7] = curve[3].y;

	prop_pressurecurve = LibinputMakeProperty(dev,
						  LIBINPUT_PROP_TABLET_TOOL_PRESSURECURVE,
						  prop_float, 32,
						  8, data);
}

static void
LibinputInitTabletAreaRatioProperty(DeviceIntPtr dev,
				    struct xf86libinput *driver_data)
{
	const struct ratio *ratio = &driver_data->options.area;
	uint32_t data[2];

	if (!want_area_handling(driver_data))
		return;

	data[0] = ratio->x;
	data[1] = ratio->y;

	prop_area_ratio = LibinputMakeProperty(dev,
					       LIBINPUT_PROP_TABLET_TOOL_AREA_RATIO,
					       XA_CARDINAL, 32,
					       2, data);
}

static void
LibinputInitProperty(DeviceIntPtr dev)
{
	InputInfoPtr pInfo  = dev->public.devicePrivate;
	struct xf86libinput *driver_data = pInfo->private;
	struct libinput_device *device = driver_data->shared_device->device;
	const char *device_node;
	CARD32 product[2];
	int rc;

	prop_float = XIGetKnownProperty("FLOAT");

	LibinputInitTapProperty(dev, driver_data, device);
	LibinputInitTapDragProperty(dev, driver_data, device);
	LibinputInitTapDragLockProperty(dev, driver_data, device);
	LibinputInitTapButtonmapProperty(dev, driver_data, device);
	LibinputInitNaturalScrollProperty(dev, driver_data, device);
	LibinputInitDisableWhileTypingProperty(dev, driver_data, device);
	LibinputInitScrollMethodsProperty(dev, driver_data, device);
	LibinputInitClickMethodsProperty(dev, driver_data, device);
	LibinputInitMiddleEmulationProperty(dev, driver_data, device);
	LibinputInitRotationAngleProperty(dev, driver_data, device);
	LibinputInitAccelProperty(dev, driver_data, device);
	LibinputInitCalibrationProperty(dev, driver_data, device);
	LibinputInitLeftHandedProperty(dev, driver_data, device);
	LibinputInitModeGroupProperties(dev, driver_data, device);
	LibinputInitSendEventsProperty(dev, driver_data, device);

	/* Device node property, read-only  */
	device_node = driver_data->path;
	prop_device = MakeAtom(XI_PROP_DEVICE_NODE,
			       strlen(XI_PROP_DEVICE_NODE),
			       TRUE);
	rc = XIChangeDeviceProperty(dev, prop_device, XA_STRING, 8,
				    PropModeReplace,
				    strlen(device_node), device_node,
				    FALSE);
	if (rc != Success)
		return;

	XISetDevicePropertyDeletable(dev, prop_device, FALSE);

	prop_product_id = MakeAtom(XI_PROP_PRODUCT_ID,
				   strlen(XI_PROP_PRODUCT_ID),
				   TRUE);
	product[0] = libinput_device_get_id_vendor(device);
	product[1] = libinput_device_get_id_product(device);
	rc = XIChangeDeviceProperty(dev, prop_product_id, XA_INTEGER, 32,
				    PropModeReplace, 2, product, FALSE);
	if (rc != Success)
		return;

	XISetDevicePropertyDeletable(dev, prop_product_id, FALSE);

	LibinputInitDragLockProperty(dev, driver_data);
	LibinputInitHorizScrollProperty(dev, driver_data);
	LibinputInitScrollPixelDistanceProperty(dev, driver_data, device);
	LibinputInitPressureCurveProperty(dev, driver_data);
	LibinputInitTabletAreaRatioProperty(dev, driver_data);
}
