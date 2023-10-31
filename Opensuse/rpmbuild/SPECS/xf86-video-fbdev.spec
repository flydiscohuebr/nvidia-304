#
# spec file for package xf86-video-fbdev
#
# Copyright (c) 2022 SUSE LLC
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


Name:           xf86-video-fbdev
Version:        0.5.0
Release:        36.14
Summary:        Framebuffer video driver for the Xorg X server
License:        MIT
Group:          System/X11/Servers/XF86_4
URL:            https://xorg.freedesktop.org/
Source0:        https://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.bz2
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(fontsproto)
BuildRequires:  pkgconfig(pciaccess) >= 0.8.0
BuildRequires:  pkgconfig(randrproto)
BuildRequires:  pkgconfig(renderproto)
BuildRequires:  pkgconfig(videoproto)
BuildRequires:  pkgconfig(xorg-macros) >= 1.8
BuildRequires:  pkgconfig(xorg-server) >= 1.0.99.901
BuildRequires:  pkgconfig(xproto)
Supplements:    xorg-x11-server
# This was part of the xorg-x11-driver-video package up to version 7.6
Conflicts:      xorg-x11-driver-video <= 7.6
ExcludeArch:    s390 s390x
%{x11_abi_videodrv_req}

%description
fbdev is an Xorg driver for framebuffer devices.

This is a non-accelerated driver, the following framebuffer depths are
supported: 8, 15, 16, 24. All visual types are supported for depth 8,
and TrueColor visual is supported for the other depths. Multi-head
configurations are supported.

%prep
%setup -q

%build
# We have some -z now related errors during X default startup (boo#1197994):
# this is directly visible on startup, so easy to test later on.
export SUSE_ZNOW=0
%configure
%make_build

%install
%make_install
find %{buildroot} -type f -name "*.la" -delete -print

%files
%license COPYING
%doc ChangeLog README
%dir %{_libdir}/xorg/modules/drivers
%{_libdir}/xorg/modules/drivers/fbdev_drv.so
%{_mandir}/man4/fbdev.4%{?ext_man}

%changelog
* Sat May 14 2022 Stefan Dirsch <sndirsch@suse.com>
- set SUSE_ZNOW to 0 (boo#1197994)
* Wed Apr 21 2021 Dirk Müller <dmueller@suse.com>
- modernize spec file:
  * move license to license dir
  * use spec-cleaner induced cleanups
* Mon Jun  4 2018 sndirsch@suse.com
- Update to version 0.5.0
  * Compatibility updates for xserver 1.20.
- supersedes the following patches
  * U_01-Default-to-32bpp-if-the-console-is-8bpp-and-we-weren-t-told-otherwise.patch
  * U_02-Use-own-thunk-functions-instead-of-fbdevHW-Weak.patch
  * U_03-Pass-the-pci-device-if-any-through-to-fbdevhw-in-probe-and-preinit.patch
  * U_04-Initialize-pci_dev.patch
  * U_05-Fix-shadow-fb-allocation-size-v2.patch
  * U_11-Remove-dead-pix24bpp-variable.patch
  * U_12-Use-shadowUpdate32to24-at-24bpp.patch
  * U_13-Use-ifdef-instead-of-if-to-avoid-build-error.patch
* Wed May 23 2018 mstaudt@suse.com
- Fix build with Xorg server 1.20 by updating to current Git.
  U_01-Default-to-32bpp-if-the-console-is-8bpp-and-we-weren-t-told-otherwise.patch
  U_02-Use-own-thunk-functions-instead-of-fbdevHW-Weak.patch
  U_03-Pass-the-pci-device-if-any-through-to-fbdevhw-in-probe-and-preinit.patch
  U_04-Initialize-pci_dev.patch
  U_05-Fix-shadow-fb-allocation-size-v2.patch
  U_11-Remove-dead-pix24bpp-variable.patch
  U_12-Use-shadowUpdate32to24-at-24bpp.patch
  U_13-Use-ifdef-instead-of-if-to-avoid-build-error.patch
* Mon May 29 2017 sndirsch@suse.com
- includes everything needed for missing sle issue entries:
  fate #320388 (bsc#1041351)
* Tue Oct 22 2013 zaitor@opensuse.org
- Update to version 0.4.4:
  + Remove mibstore.h
- Drop U_mibstore.patch, fixed upstream.
* Wed Aug  7 2013 ro@suse.de
- add ExcludeArch for s390 and s390x
* Tue Mar 19 2013 hrvoje.senjan@gmail.com
- Add U_mibstore.patch, fixes build with xorg-server 1.14
* Sun Sep  2 2012 zaitor@opensuse.org
- Update to version 0.4.3:
  + Port to new server API.
  + Convert to new screen conversion APIs.
  + Add compat-api + makefile.
  + Add MOD_CLASS_VIDEODRV to FBDevVersRec
  + Perform XV initialization only if the server supports it.
  + Avoid unused variables when XSERVER_LIBPCIACCESS is defined.
  + man: Stop mentioning server's -scanpci option.
  + Upgrade to util-macros 1.8 for additional man page support.
  + Other minor codefixes.
* Fri Apr 20 2012 vuntz@opensuse.org
- Use %%x11_abi_videodrv_req instead of static ABI Requires.
* Wed Apr 18 2012 vuntz@opensuse.org
- Split xf86-video-fbdev from xorg-x11-driver-video.
  Initial version: 0.4.2.
