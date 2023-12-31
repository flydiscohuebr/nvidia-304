#
# spec file for package xf86-input-libinput
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           xf86-input-libinput
Version:        1.1.0
Release:        93.3
Summary:        Libinput driver for the Xorg X server
License:        MIT
Group:          System/X11/Servers/XF86_4
URL:            https://xorg.freedesktop.org
Source0:        %{url}/releases/individual/driver/%{name}-%{version}.tar.gz
Source1:        %{url}/releases/individual/driver/%{name}-%{version}.tar.gz.sig
Patch0:         n_enable-tapping.patch
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(inputproto) >= 2.2
BuildRequires:  pkgconfig(libinput) >= 1.11.0
BuildRequires:  pkgconfig(xorg-macros) >= 1.13
BuildRequires:  pkgconfig(xorg-server) >= 1.10
BuildRequires:  pkgconfig(xproto)
Supplements:    xorg-x11-server
# This was part of the xorg-x11-driver-input package up to version 7.6
Conflicts:      xorg-x11-driver-input <= 7.6

%description
xf86-input-libinput is a libinput-based X.Org driver. The actual driver bit
is quite limited, most of the work is done by libinput, the driver itself
passes on the events (and wrangles them a bit where needed).

%package devel
Summary:        Libinput driver for the Xorg X server -- Development Files
Group:          Development/Libraries/X11
Requires:       %{name} = %{version}

%description devel
xf86-input-libinput is a libinput-based X.Org driver. The actual driver bit
is quite limited, most of the work is done by libinput, the driver itself
passes on the events (and wrangles them a bit where needed).

%prep
%autosetup -p1

%build
%configure --with-xorg-conf-dir="%{_datadir}/X11/xorg.conf.d/"
%make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print

%files
%license COPYING*
%dir %{_libdir}/xorg/modules/input
%{_datadir}/X11/xorg.conf.d/40-libinput.conf
%dir %{_datadir}/X11/xorg.conf.d
%{_libdir}/xorg/modules/input/libinput_drv.so
%{_mandir}/man4/libinput.4%{?ext_man}

%files devel
%{_includedir}/xorg/libinput-properties.h
%{_libdir}/pkgconfig/xorg-libinput.pc

%changelog
* Tue Apr  4 2023 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.3.0
  The main feature in this version is support for the new 'custom' pointer
  acceleration profile in libinput 1.23.0. This acceleration profile is
  quite flexible, so it is exposed via several properties:
  - "libinput Accel Custom Fallback Points" and "libinput Accel Custom Fallback Step"
  - "libinput Accel Custom Motion Points" and "libinput Accel Custom Motion Step"
  - "libinput Accel Custom Scroll Points" and "libinput Accel Custom Scroll Points"
  For details on what these mean, please see the man page and the
  libinput documentation:
  https://wayland.freedesktop.org/libinput/doc/latest/pointer-acceleration.html
  In addition, the "libinput Accel Profiles Available" and
  "libinput Accel Profile Enabled" properties have been expanded to 3 values. For
  backwards compatibility, the "libinput Accel Profile Enabled" continues
  to support setting 2 values only.
* Tue Jan 25 2022 Bjørn Lie <bjorn.lie@gmail.com>
- Enable tarball sig url too, verify tarball via keyring.
* Mon Jan 24 2022 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.2.1
  * few typos and misc minor fixes
  * property added to turn off new high-resolution wheel scrolling
    API
* Fri Nov 19 2021 Stefan Dirsch <sndirsch@suse.com>
- enable build on s390x (JIRA#SLE-18632)
* Fri Oct  8 2021 Stefan Dirsch <sndirsch@suse.com>
- reverted previous change; the issue was broken ckb-next, not
  the usage of libinput v120 API (boo#1190646)
* Tue Oct  5 2021 Stefan Dirsch <sndirsch@suse.com>
- switch to libinput v120 API broke the driver, so disable it for
  now via patching config.h in specfile after running configure
  (boo#1190646)
* Mon Sep 20 2021 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.2.0
  * This release introduces support for touchpad gestures that will
    be available as part of X server 21.1. Additionally high-resolution
    scrolling data is now acquired from libinput if available and sent
    downstream to X server. The default scroll distance has been bumped
    to 120 in the process, but this should not affect correctly written
    clients.
* Wed Jun 23 2021 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.1.0
  * This release adds a new driver-specific option:
    ScrollPixelDistance. This option converts movement "pixels"
    from libinput into the server's "scroll unit" definition and
    can thus help speeding up or slowing down two-finger/edge scrolling.
* Fri Apr 16 2021 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.0.1
  * Only one fix, the code to set the tap button mapping property
    didn't correctly check for a valid device, causing memory
    corruption and a crash if called after a device was disabled.
    Or, in more user-friendly terms: if your X session crashed
    after calling `xinput disable $touchpad-device`, this release
    has the fix for it.
* Tue Apr  6 2021 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.0.0
  * The biggest change here is the license change to MIT. Due to an unfortunate
    copy/paste error, the actual license text used was the Historical Permission
    Notice and Disclaimer license. With the ack of the various contributors, the
    driver is now using the MIT license text as intended. The actual impact is
    low, the HPND is virtually identical to the MIT license anyway (ianal,
    consult your legal dept if you have one).
  * The only other notable change: cancelled touch points are now lifted
    correctly. Where libinput cancels a touch, e.g. in response to a palm being
    detected, the touch point previously got stuck in the down state. This is
    fixed now.
* Fri Mar 12 2021 Dirk Müller <dmueller@suse.com>
- refresh spec file (move licenses to licensedir)
* Tue May 19 2020 Stefan Dirsch <sndirsch@suse.com>
- Update to version 0.30.0
  * Only one noticeable change: the scroll button lock
    configuration option available in recent libinput versions
    is now exposed as the usual set of properties by this driver.
* Tue Aug 20 2019 Stefan Dirsch <sndirsch@suse.com>
- Update to version 0.29.0
  * Only one real fix: we now check for the tool type as well as
    the serial when we create subdevices for tablet tools.
    Previously there were some cases where the eraser device
    wasn't created correctly.
* Tue Jul 30 2019 Stefan Dirsch <sndirsch@suse.com>
- move xorg.conf.d snippet from /etc/X11/xorg.conf.d to
  /usr/share/X11/xorg.conf.d (boo#1139692)
* Mon Feb  4 2019 sndirsch@suse.com
- Update to version 0.28.2
  * This release contains a bugfix that will likely trigger in future releases
    of libinput. The driver assumed wrongly that any wheel event has a nonzero
    discrete event and used the discrete as a divisor. Which is obviously a bad
    idea, mathematically speaking, because you never know what the future will
    bring. Hint: it will bring wheel events with a discrete of zero.
* Mon Oct 15 2018 sndirsch@suse.com
- Update to version 0.28.1
  * Only two commits, only one that really matters: previously the
    driver used the per-device slot number to fetch the tracking IDs
    from a driver-internal array. Because devices re-use slots, this
    could cause a tracking ID mismatch when two touchscreens had the
    finger down at the same time. This is now fixed by switching to
    libinput's seat-wide slot number instead.
* Wed Jul 11 2018 sndirsch@suse.com
- Update to version 0.28.0
  * This version adds a feature to expose the touch count for touch
    devices through the X device. It makes it possible for clients
    to adjust their UI based on the number of supported touches by
    this device.
  * Also, the draglock code had a bug and would call memset with
    an invalid size, causing memory corruption. You're advised to
    update, especially if you expect someone to use the draglock
    options.
* Thu Apr 12 2018 sndirsch@suse.com
- Update to version 0.27.1
  * Just one bugfix, a regression introduced by the new property
    handling in 0.27.0 caused the property to toggle left-handed
    to not be initialized on all devices that required it.
- supersedes U_Fix-left-handed-property.patch
* Thu Apr  5 2018 bjorn.lie@gmail.com
- Add U_Fix-left-handed-property.patch: Fix "left handed" property
  not set on all pointers (fdo#105667).
* Wed Apr  4 2018 sndirsch@suse.com
- Update to version 0.27
  * The libinput driver splits libinput devices into multiple X
    devices (e.g. a mouse and a keyboard device) and then routes
    the events accordingly. In the case where there is a user-
    specific on one device, a VT switch or suspend/resume cycle
    sometimes overwrote the configuration with the devices
    in-order, resulting in the loss of that configuration. e.g.
    if the keyboard device resumes after the mouse device, the
    natural scroll setting may get overwritten with the default.
    This is fixed now.
    And a note to the man page, we don't support specifying
    devices as /dev/input/by-id or /dev/input/by-path. It's not
    worth the effort, so at least point this out in the man page.
* Tue Sep 19 2017 sndirsch@suse.com
- Update to version 0.26
  * A few patches that have been sitting on master for a while, of
    which two are documentation patches. The most interesting patch
    is for tablets: previously we didn't send a separate motion
    event before the button event which caused some clients to
    trigger the button event on the previous stylus position.
- obsoletes U_Only-initialize-properties.patch
* Fri Sep  1 2017 zaitor@opensuse.org
- Add U_Only-initialize-properties.patch: Only initialize
  properties that match capabilities on a subdevice (fdo#100900).
* Fri May 19 2017 sndirsch@suse.com
- Leap 42.3 merge
  * boo#1039812
* Fri May  5 2017 sndirsch@suse.com
- Update to version 0.25.1
  * Just one patch that's been sitting on master for a while now -
    after a proximity event we immediately post a motion event.
    This avoids the lines between the last known point before
    proximity out and the new point.
* Thu Mar  9 2017 sndirsch@suse.com
- Update to version 0.25.0
  * fixing two bugs with tablet pad modes on kernel 4.9 and later.
    First, we never successfully opened the sysfs files representing
    the LEDs, so they didn't update as the kernel would change them.
    Second, had we opened them correctly we would've likely crashed
    as the property update would have been sent from within the
    input thread.  Both issues are fixed now, together with a fix
    for a test case failure for ppc64/aarch64.
* Mon Feb 20 2017 zaitor@opensuse.org
- Update to version 0.24.0:
  + Tablets now support a configurable pressure curve.
  + Tablets now have a 'area ratio' setting to be able to match the
    tablet aspect ratio with that of the screen.
  + The mouse wheel's click angle now (correctly) affects how fast
    the scroll wheel triggers. In particular, if you have a wheel
    with a very small click angle, it won't trigger for every click
    anymore.
* Mon Dec 12 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 0.23.0:
  A couple of cleanups, no big features added. Most of this was in
  the property handling code. The most visible fix is that we now
  handle addition of initially disabled devices correctly, i.e.
  when a device is plugged in while the server is VT-switched
  away. In the non-logind case this previously caused a segfault.
  Our tablet support is good enough that we now match against
  tablets too. The xorg.conf.d sort order means that if you have
  the wacom driver installed, that driver will take over.
  Otherwise, libinput will handle tablets.
* Fri Oct 21 2016 zaitor@opensuse.org
- Update to version 0.22.0:
  + Fix the new tap button map option handling.
  + When the first device was removed (and subsequently freed by
    the server) the input thread would continue to call that
    device's read_input() func, eventually causing a crash.
- Drop
  U_xf86-input-libinput-Fix_tap_button_map_option_handling.patch:
  Fixed upstream.
* Sat Oct 15 2016 zaitor@opensuse.org
- Add upstream patch to fix touchpad when lmr option is used:
  U_xf86-input-libinput-Fix_tap_button_map_option_handling.patch.
  Fixes fdo#97989.
* Fri Sep 30 2016 zaitor@opensuse.org
- Update to version 0.20.0:
  + Most important fix is the use of input_lock() instead of the
    old SIGIO stuff to handle the input thread in server 1.19.
  + This version now supports tablet pads and exposes properties
    for changing the tap button mapping and the rotation.
- Rebase n_enable-tapping.patch.
- Pass --with-xorg-conf-dir to configure and modify spec following
  upstream changes.
* Tue Sep 20 2016 sndirsch@suse.com
- install the driver by default; added "Supplements: xorg-x11-server"
  for this (bnc#999098)
* Thu Sep 15 2016 zaitor@opensuse.org
- Update to version 0.19.1:
  + One of the property names had a clear typo in it, "Horizonal"
    instead of "Horizontal". This update corrects this property
    name.
  + A second patch was snuck in to avoid bug messages when
    submitting button numbers beyond what we can handle in the
    protocol.
* Thu Apr 28 2016 sndirsch@suse.com
- Update to version 0.19.0
  One significant change that affects packagers: the config snippet has been
  renamed from 90-libinput.conf to 60-libinput.conf.
  This should not show any immediate effects on most user's machines but there
  is a slight potential of user configurations to change if their custom
  snippets now sort after libinput instead of before.
  This change is part of the two-step solution to fix the handling of wacom
  tablets when the libinput driver is present. Previously, the libinput driver
  would overwrite any driver assigned to any supported devices. While it does
  not yet bind to tablet devices by default, some tablets also look like
  a keyboard, causing those devices to stop working. For those devices, the
  wacom driver is the better option.
  Since the X server is lacking an option to conditionally bind InputClass
  snippets based on current values (git master has a NoMatch* option), the
  safe alternative is to bump the libinput priority down and, at the same
  time, bump the wacom driver's priority up.
  For the cases where the wacom driver should not handle any device, simply
  uninstalling it is sufficient.
- refreshed n_enable-tapping.patch
* Thu Apr  7 2016 sndirsch@suse.com
- Update to version 0.18.0:
  This release adds support for tablet tool devices. Now, this support should
  be taken with a grain of salt, it works differently to the xf86-input-wacom
  driver and thus some capability differences can be observed:
  First, pad support is still missing, i.e. you cannot use the buttons on the
  tablet bit itself.
  There are no specific configuration options just yet, and the way we are
  aiming for libinput support, many of the options you are used to may not
  exist ever.
  The most important part: tool support is handled dynamically. As a tool is
  first brought into proximity, a new X device is created for that tool only
  (no multiplexing of tools through the same X device). Clients may expect a
  static list of tools, so for those you will need to bring the tool into
  proximity before starting the client.
  In short, do not use this driver for tablets on production workstations yet.
* Fri Feb 26 2016 zaitor@opensuse.org
- Update to version 0.17.0:
  + Fix compiler warnings about missing tablet event cases.
  + Add property/option for enabling/disabling tap-n-drag.
  + Fix default tapping drag lock property value.
  + Allow hotplugging a device immediately.
  + Change creating subdevices to something more generic.
* Thu Dec 24 2015 tobias.johannes.klausmann@mni.thm.de
- Update to version 0.16.0:
  This release fixes a long-standing issue with mixed devices that expose a
  pointer and a keyboard interface at the same time. X requires a strict
  separation between pointers and keyboards, these devices were usually
  initialized as pointers and exhibited some keyboard functionality issues
  (e.g. XKB layouts didn't get applied correctly). With this release, the xorg
  libinput driver splits such devices into multiple X devices, one for the
  keyboard and one for the pointer, routing the events as necessary and thus
  fixing those issues.
- Changes to package:
  + Remove patch U_xf86_input_libinput_mem_leak_fix.patch: included in this
    release.
* Tue Dec 15 2015 zaitor@opensuse.org
- Add U_xf86_input_libinput_mem_leak_fix.patch: Plug two memory
  leaks, patch from upstream git.
- Correct minimum version of BuildRequires pkgconfig(libinput).
* Wed Oct 28 2015 sndirsch@suse.com
- Update to version 0.15.0:
  This release adds new properties to select the pointer acceleration profile.
  See the libinput documentation for more details
  http://wayland.freedesktop.org/libinput/doc/latest/pointer-acceleration.html
  Note that this driver now installs a xorg.conf.d snippet in the usual
  locations. This snippet will assign libinput to mouse, touchpad, keyboard
  and touch devices but will skip tablets and joysticks (we don't support
  thoss in libinput yet). The filename of the snippet means it will sort after
  evdev and synaptics and thus override either driver.
- n_enable-tapping.patch
  * enables tapping for touchpads in upstream xorg.conf.d snippet
- removed superseded xorg.conf.d snippet
* Sun Sep 27 2015 mpluskal@suse.com
- Add gpg signature
* Mon Aug 31 2015 zaitor@opensuse.org
- Update to version 0.14.0:
  + Rename a local variable to not shadow the BSD strmode(3)
    function.
  + Remove unneeded header, epoll(7) interface is not directly
    used.
  + Rename main source file to x86libinput.c.
  + gitignore: add patterns for automake test suite and misc other
    bits.
  + Add drag lock support.
  + Add an option to disable horizontal scrolling.
  + Revamp server fd opening.
  + Use xf86OpenSerial instead of a direct open() call.
  + Fix typo in libinput.man.
* Tue Aug  4 2015 zaitor@opensuse.org
- Update to version 0.13.0:
  + Fix compiler warnings about touchpad gestures.
  + man: minor man page improvements.
  + Add a property for Disable While Typing.
* Sat Jul 25 2015 zaitor@opensuse.org
- Update to version 0.12.0:
  + Support buttons > BTN_BACK on mice.
  + Add a property for tap drag lock.
- Drop autoconf, automake and libtool BuildRequires, also stop
  running autoreconf before configure. They were needed in the past
  but we do not carry any patches anymore.
- Remove emtpy post/postun sections.
* Sun Jun  7 2015 zaitor@opensuse.org
- Update to version 0.11.0:
  + Only init abs axes if we don't have acceleration.
  + Use the new unaccelerated valuator ValuatorMask features.
  + Fix missing scroll methods default/scroll button property.
* Sat May 23 2015 zaitor@opensuse.org
- Update to version 0.10.0:
  + Group scroll distances into a struct.
  + Add option "ButtonMapping" (fdo#90206).
  + man: add two linebreaks to make things easier to visually
    parse.
  + Move the option parsing into helper functions.
  + Add a property for middle button emulation.
* Fri Apr 24 2015 sndirsch@suse.com
- xf86-input-libinput 0.9.0
  * A couple of cosmetic changes but one addition of a new set of
    properties: properties named "libinput something Default" show
    the libinput default for a device. For example:
    libinput Click Methods Available (284): 1, 1
    libinput Click Method Enabled (285):    0, 1
    libinput Click Method Enabled Default (286):    1, 0
    This device has software buttons and clickfingers available,
    clickfingers is currently enabled, software buttons is the
    default for this device.
* Wed Apr 22 2015 sndirsch@suse.com
- no longer install driver package by default, i.e. commented out
  "Supplements: xorg-x11-server" in specfile
- 90-libinput.conf: enable tapping on touchpads by default
  (http://lists.opensuse.org/opensuse-factory/2015-04/msg00233.html)
* Tue Apr 14 2015 hrvoje.senjan@gmail.com
- Install license in main package
- Install 90-libinput.conf config file (boo#926942)
* Fri Mar 20 2015 tobias.johannes.klausmann@mni.thm.de
- New package xf86-input-libinput with initial version 0.8.0:
  xf86-input-libinput is a libinput-based X.Org driver. The actual driver bit
  is quite limited, most of the work is done by libinput, the driver itself
  passes on the events (and wrangles them a bit where needed).
