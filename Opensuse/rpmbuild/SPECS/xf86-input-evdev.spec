#
# spec file for package xf86-input-evdev
#
# Copyright (c) 2021 SUSE LLC
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


Name:           xf86-input-evdev
Version:        2.10.6
Release:        91.24
Summary:        Generic Linux input driver for the Xorg X server
License:        MIT
Group:          System/X11/Servers/XF86_4
URL:            https://xorg.freedesktop.org/
Source0:        https://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.bz2
Source1:        https://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.bz2.sig
Source2:        %{name}.keyring
Source3:        11-evdev.conf
Source4:        50-elotouch.conf
Patch1:         u_01-Add-a-kiosk-mode-for-touch-screens.patch
Patch2:         u_02-Add-delay-between-button-press-and-release-to-kiosk-mode.patch
# Next three lines are needed for u_01-Add-a-kiosk-mode-for-touch-screens.patch
BuildRequires:  autoconf >= 2.60
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(inputproto)
BuildRequires:  pkgconfig(libevdev) >= 0.4
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(mtdev)
BuildRequires:  pkgconfig(xorg-macros) >= 1.8
BuildRequires:  pkgconfig(xorg-server)
BuildRequires:  pkgconfig(xproto)
Requires:       udev
Supplements:    xorg-x11-server
# This was part of the xorg-x11-driver-input package up to version 7.6
Conflicts:      xorg-x11-driver-input <= 7.6
Provides:       x11-input-mtrack
Obsoletes:      x11-input-mtrack
ExcludeArch:    s390 s390x

%description
evdev is an Xorg input driver for Linux's generic event devices. It
therefore supports all input devices that the kernel knows about,
including most mice, keyboards, tablets and touchscreens.

%package devel
Summary:        Generic Linux input driver for the Xorg X server -- Development Files
Group:          Development/Libraries/X11
Requires:       %{name} = %{version}

%description devel
evdev is an Xorg input driver for Linux's generic event devices. It
therefore supports all input devices that the kernel knows about,
including most mice, keyboards, tablets and touchscreens.

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
# Once u_01-Add-a-kiosk-mode-for-touch-screens.patch is removed this is no longer needed
%{_bindir}/autoreconf -v --install --force
%configure
%make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print
install -D -m 644 %{SOURCE3} %{SOURCE4} %{buildroot}/%{_datadir}/X11/xorg.conf.d/

%post
# re-plug the input devices
udevadm trigger --subsystem-match=input --action=change || :

%postun
# re-plug the input devices
udevadm trigger --subsystem-match=input --action=change || :

%files
%license COPYING
%doc README
%dir %{_datadir}/X11/xorg.conf.d
%{_datadir}/X11/xorg.conf.d/*.conf
%dir %{_libdir}/xorg/modules/input
%{_libdir}/xorg/modules/input/evdev_drv.so
%{_mandir}/man4/evdev.4%{?ext_man}

%files devel
%{_includedir}/xorg/evdev-properties.h
%{_libdir}/pkgconfig/xorg-evdev.pc

%changelog
* Fri Mar 12 2021 Dirk Müller <dmueller@suse.com>
- refresh spec file (move licenes)
* Tue Jul 30 2019 Stefan Dirsch <sndirsch@suse.com>
- move all xorg.conf.d snippets from /etc/X11/xorg.conf.d to
  /usr/share/X11/xorg.conf.d (boo#1139692)
* Wed May 30 2018 sndirsch@suse.com
- upt to version 2.10.6
  * Since evdev is in maintenance mode there aren't a lot of
    features to go around but still a few important fixes. Andrey
    fixed the proximity event generation for tablets and the
    handling of devices without axes but buttons - previously
    those were assumed to be keyboards in the server. Better
    error reporting from Christian and the rest are build system
    fixes that went into all xorg repositories.
* Mon May 29 2017 sndirsch@suse.com
- includes everything needed for missing sle issue entries:
  fate #320263, fate#315643-315645, 319159-319161, 319618 (bsc#1041371)
- 50-elotouch.conf: Make sure an 'TouchSystems CarrollTouch 4500U'
  is an absolute device (bnc#876089, bsc#1041371)
* Thu Jan 19 2017 sndirsch@suse.com
- update to version 2.10.5
  * Two fixes, one new feature for the evdev driver. The new
    feature is the ability to change the emulated middle button
    number (e.g. useful on devices with physical middle button
    as well).
* Sat Oct  1 2016 mimi.vx@gmail.com
- update to version 2.10.4
  * Support XINPUT ABI version 23 and 24
* Wed Jun  1 2016 sndirsch@suse.com
- Update to version 2.10.3
  * Only one fix over 2.10.2 restoring tablets' functionality. A
    bug in the wheel emulation rework caused non-x/y axes to stop
    updating. Interaction with tablets thus resulted in a zero
    pressure sent to the clients an the tablet being unable to draw.
* Mon May 23 2016 eich@suse.com
- u_01-Add-a-kiosk-mode-for-touch-screens.patch
  u_02-Add-delay-between-button-press-and-release-to-kiosk-mode.patch
  (FATE#320263).
* Mon May  2 2016 eich@suse.com
- u_01-Add-a-kiosk-mode-for-touch-screens.patch
  u_02-Add-delay-between-button-press-and-release-to-kiosk-mode.patch
  Add click on touch (FATE#320263).
* Fri Apr 29 2016 sndirsch@suse.com
- Update to version 2.10.2
  This release restores wheel emulation on absolute devices and drops the
  forced direction locking for scroll buildup during wheel emulation since it
  made it almost impossible to actually scroll in both directions. Since
  horizontal scrolling is disabled by default anyway, we don't need this lock.
* Fri Jan  8 2016 sndirsch@suse.com
- Update to version 2.10.1
  Only one change over 2.10, affecting some devices with absolute axes but not
  ABS_X/ABS_Y. Previously, those devices had the first to axes mapped to axes
  0 and 1 and thus some random axes was interpreted as x/y coordinate. With
  this release, axes 0 and 1 are reserved for x/y axes only.
* Fri Nov 13 2015 mpluskal@suse.com
- Use url for source
- Add gpg signature
- Make building more verbose
* Wed Oct 28 2015 sndirsch@suse.com
- Update to version 2.10.0
  Plenty of bugfixes accumulated over time, one new option is now
  available: Resolution. This enables a user to set a mouse device's
  native resolution, if set the device's deltas are scaled to a
  normalized 1000dpi resolution. This can be used to make
  high-resolution mice less sensitive without having to actually
  change the acceleration in the desktop environment. The default
  for this option is 0 and no scaling is performed.
* Fri Jul 31 2015 jengelh@inai.de
- Ignore absence of udevadm, it won't be present in the build env.
* Tue Mar 31 2015 sndirsch@suse.com
- Update to version 2.9.2
  * Two fixes in this release, one to support Android MT devices,
    one to avoid an array index overflow.
* Sat Nov 29 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.9.1:
  This release fixes a couple of bugs with absolute devices that
  have scroll wheels (such as the qemu tablets devices) and avoids
  the "unable to find touch point 0" warnings previously caused by
  a touch starting before the device was enabled.
* Wed Jul 30 2014 stefan.bruens@rwth-aachen.de
- enable multitouch support (missing libmtdev build dependency),
  fixes bnc#889469
* Tue May 20 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.9.0:
  Use the server's device list for duplicate detection (FDO#78309)
* Wed May  7 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.8.99.1 (2.9RC1)
  The first evdev 2.9 Snapshot.
  The biggest changes are the switch to libevdev and support for
  server-managed fds. The latter needs server support, so don't
  expect it to work on anything but git master.
* Wed May  7 2014 sndirsch@suse.com
- Update to version 2.8.3
  * Only two changes, the REL_DIAL fix restores proper horizontal
    scrolling behaviour to a set of Microsoft mice.
* Wed Mar 19 2014 sndirsch@suse.com
- 11-evdev.conf: enable emulate3buttons on trackpoint devices
  (bnc#869097)
* Mon Feb 10 2014 sndirsch@suse.com
- 11-evdev.conf: emulate wheelbutton for another trackpoint device
  (bnc#861813)
* Fri Dec 20 2013 sndirsch@suse.com
- provides/obsoletes x11-input-mtrack, since multitouch devices
  are now covered via mtdev library; drop request for
  x11-input-mtrack has been filed
* Mon Oct 14 2013 sndirsch@suse.com
- added 11-evdev.conf xorg.conf.d snippet, since apparently some
  tweaks are still required (bnc#843333)
* Sun Oct  6 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.8.2:
  Second release for evdev 2.8 is now available. Two minor but important
  fixes. Evdev now writes SYN_REPORT after toggling LEDs, so other processes
  listening in on the device can see the change immediately. The other fix
  addresses an inconsistency in the mapping of REL_DIAL.
- Remove upstream patches:
  + Patch1: U_0001-Write-a-SYN_REPORT-after-the-last-LED.patch
  + Patch2: U_0002-Don-t-use-mtdev-for-protocol-B-devices.patch
  + Patch3: U_0003-Remove-a-comment.patch
* Thu Sep  5 2013 sndirsch@suse.com
- U_0001-Write-a-SYN_REPORT-after-the-last-LED.patch
  * Write a SYN_REPORT after the last LED
- U_0002-Don-t-use-mtdev-for-protocol-B-devices.patch
  * Don't use mtdev for protocol B devices
- U_0003-Remove-a-comment.patch
  * Remove a comment
* Thu Sep  5 2013 sndirsch@suse.com
- build driver with mtdev support (multitouch devices)
* Thu Jul 11 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.8.1:
  A new option was added, "TypeName" defines the
  XI device type provided in the XListInputDevices() reply.
  Two fixes, one for a set of MT devices without legacy axes, one for a
  misconfiguration (inertia of 0 should be no inertia).
  Switch default model to pc104, but the switch to pc104 has no effect,
  it's merely to make it more explicit.
* Tue Mar 26 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.8.0:
  Not a whole lot of new things happening here, mostly
  cleanup and various misc fixes. Most bugfixes have already found their way
  into the 2.7.x releases.
- Notable changes:
  + axis swap/inversion and calibration is now possible for touch events too
    (#59340)
  + maintainer-mode is now always enabled
  + evdev uses sigsafe logging if available
- Remove upstreamed patches:
  + evdev_move-valuator-swapping-into-a-helper-function.patch (patch0)
  + evdev_move-calibration-asjustments-to-helper-function.patch (patch1)
  + evdev_handle-axis-swap-calibration-and-inversion-for-touch-events.patch (patch2)
* Tue Jan 15 2013 msrb@suse.com
- evdev_handle-axis-swap-calibration-and-inversion-for-touch-events.patch,
  evdev_move-calibration-asjustments-to-helper-function.patch,
  evdev_move-valuator-swapping-into-a-helper-function.patch
  * Handle axis swap, calibration and inversion for touch events
    (bnc#785508)
* Thu Nov 22 2012 tobias.johannes.klausmann@mni.thm.de
- Use static tarballs instead of git created ones and remove
  unneeded dependencies!
* Mon Aug 13 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.7.3:
  + Three bugfixes, one fixes a regression introduced in 2.7.2.
* Sat Aug  4 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.7.2:
  + This update fixes a few compiler warnings and a memory leak.
* Tue Jul 24 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.7.1:
  + First update to the evdev 2.7 series. This update fixes a couple
    of bugs and memory leaks.
* Thu Apr 19 2012 dimstar@opensuse.org
- Update to version 2.7.0:
  + Only force REL_X/Y if no ABS_X/Y exists
  + Copy last valuator values into new touch valuator masks
  + Prefere relative axis labelling over absolute axis labelling
  + Force x/y axes to exist on devices with any other axes
    (fdo#44655)
- Add pkgconfig(libudev) BuildRequires: New dependency
- Add pkgconfig(mtdev) BuildRequires: Support Multi-Touch.
- Use %%x11_abi_xinpot_req instead of static ABI Requires.
* Wed Apr 18 2012 vuntz@opensuse.org
- Split xf86-input-evdev from xorg-x11-driver-input.
  Initial version: 2.6.0.
