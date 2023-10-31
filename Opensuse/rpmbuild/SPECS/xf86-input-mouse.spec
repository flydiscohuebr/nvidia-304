#
# spec file for package xf86-input-mouse
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


Name:           xf86-input-mouse
Version:        1.9.5
Release:        36.2
Summary:        Mouse input driver for the Xorg X server
License:        MIT
Group:          System/X11/Servers/XF86_4
URL:            http://xorg.freedesktop.org/
Source0:        http://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.xz

BuildRequires:  autoconf >= 2.60
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pkg-config
BuildRequires:  pkgconfig(inputproto)
BuildRequires:  pkgconfig(xorg-macros) >= 1.8
BuildRequires:  pkgconfig(xorg-server) >= 1.5.99.901
BuildRequires:  pkgconfig(xproto)
Requires:       udev
Enhances:       xorg-x11-server
# This was part of the xorg-x11-driver-input package up to version 7.6
Conflicts:      xorg-x11-driver-input <= 7.6
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
ExcludeArch:    s390 s390x

%description
mouse is an Xorg input driver for mice. The driver supports most
available mouse types and interfaces, though the level of support for
types of mice depends on the OS.

%package devel
Summary:        Development files for the Mouse input driver
Group:          Development/Libraries/X11
Requires:       %name >= %version

%description devel
Development files for the Mouse input driver for the Xorg X server.

%prep
%setup -q

%build
autoreconf -fi
%configure
make %{?_smp_mflags}

%install
%make_install
find %{buildroot}%{_libdir} -name '*.la' -type f -delete -print

%post
# re-plug the input devices
udevadm trigger --subsystem-match=input --action=change || :

%postun
# re-plug the input devices
udevadm trigger --subsystem-match=input --action=change || :

%files
%defattr(-,root,root)
%doc README
%license COPYING
%dir %{_libdir}/xorg/modules/input
%{_libdir}/xorg/modules/input/mouse_drv.so
%{_datadir}/man/man4/mousedrv.4%{?ext_man}

%files devel
%defattr(-,root,root)
%{_includedir}/xorg/xf86*.h
%{_libdir}/pkgconfig/*.pc

%changelog
* Fri May  5 2023 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.9.5
  * sun_mouse: include more required system headers
  * sun_mouse: Add RelToAbs option to convert relative events to absolute
  * sun_mouse: remove entry from vuidMouseList in DEVICE_CLOSE
  * Remove "All rights reserved" from Oracle copyright notices
  * Rearrange includes to fix build on OmniOS. Include unistd.h for ioctl(2).
* Wed Nov  2 2022 Stefan Dirsch <sndirsch@suse.com>
- Update to version 1.9.4
  * Update configure.ac bug URL for gitlab migration
  * Fix spelling/wording issues
  * gitlab CI: add a basic build test
  * gitlab CI: stop requiring Signed-off-by in commits
  * sun_mouse: Fix -Wsign-compare warnings
  * sun_mouse: Fix -Wnull-dereference warning
  * checkForErraticMovements: Fix -Wempty-body warnings
  * SetupMouse: fix -Wsign-compare warning
  * InputDriverRec: Fix -Wmissing-field-initializers warning
  * autoGood: quiet -Wimplicit-fallthrough warning
  * configure: check for timingsafe_memcmp
  * sun_mouse.c: #include "config.h"
* Thu Apr  9 2020 Stefan Brüns <stefan.bruens@rwth-aachen.de>
- Downgrade Supplements: xorg-x11-server to Enhances, to avoid the
  package being pulled in by default. Contemporary mice are
  handled by xf86-input-evdev or xf86-input-libinput.
* Tue Jun 19 2018 sndirsch@suse.com
- Update to version 1.9.3
  * For Xserver 1.20 compatibility.
- supersedes U_adapt-to-removal-of-xf86GetOS.patch
* Mon Oct  9 2017 tobias.johannes.klausmann@mni.thm.de
- Add patch U_adapt-to-removal-of-xf86GetOS.patch
  This patch is in preparation of the upcoming XServer release
* Sat Nov 19 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.9.2:
  This release supports the X server 1.19.
* Fri Jul 31 2015 jengelh@inai.de
- Ignore absence of udevadm, it won't be present in the build env.
* Tue Dec 16 2014 zaitor@opensuse.org
- Update to version 1.9.1:
  + Update some outdated language in a comment on obsolete
    hardware.
  + Make absolute input reporting in Solaris aware of resolution
    changes.
  + Do not drop the result of protocol detection.
  + Add support for absolute positioning (tablets).
  + For wsmouse, keep 3-button emulation status.
  + Make wsmouse (re-)init the version.
  + Enable MSE_MISC on NetBSD as well. Otherwise we can't find
    WSMouse.
  + Add AC_SYSTEM_EXTENSIONS to expose asprintf with GNU libc.
  + Use asprintf (or Xprintf on old servers) instead of
    strdup+sprintf.
  + Wrap some overly long lines.
* Fri Sep 20 2013 sndirsch@suse.com
- removed 11-mouse.conf xorg.conf.d snippet, since now most (if not
  all) the remappings that we have there are actually defaults, so
  doing nothing.  Also I consider them outdated, no longer matching
  at all, or even completely wrong.
* Thu Mar 28 2013 zaitor@opensuse.org
- Update to version 1.9.0:
  + autogen.sh: Implement GNOME Build API.
  + configure: Drop AM_MAINTAINER_MODE.
  + Use signal-safe logging if available.
  + Fix compilation error with EXTMOUSEDEBUG on.
* Mon Sep 17 2012 sndirsch@suse.com
- 11-mouse.conf: use evdev driver also for users of Lenovo USB
  keyboards with trackpoint (bnc#780626)
* Tue Jul 31 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.8.1:
  + Fix compiler warnings
- Added a development Package
* Fri Jul 27 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.8.0:
  + drop support for Xorg 1.6.x, require Xorg 1.7 or later.
  + expose "Device Node" (read-only), "Mouse Middle Button Emulation"
    (read-write) and "Mouse Middle Button Timeout" (read-write)
    properties via the Xinput properties API to allow distinguishing
    between multiple devices and controlling the 3rd button emulation
    options at runtime, without having to edit xorg.conf.d files and
    restart the server.
* Thu Apr 19 2012 dimstar@opensuse.org
- Update to version 1.7.2:
  + minor code clean ups
  + Bug fixes
- Use %%x11_abi_xinput_req instead of static ABI Requires.
* Wed Apr 18 2012 vuntz@opensuse.org
- Split xf86-input-mouse from xorg-x11-driver-input.
  Initial version: 1.7.1.
