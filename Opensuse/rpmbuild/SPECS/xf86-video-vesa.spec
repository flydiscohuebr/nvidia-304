#
# spec file for package xf86-video-vesa
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


%{?x11_abi_has_dpms_get_capabilities: %{x11_abi_has_dpms_get_capabilities}}
Name:           xf86-video-vesa
Version:        2.6.0
Release:        50.8
Summary:        Generic VESA video driver for the Xorg X server
License:        MIT
Group:          System/X11/Servers/XF86_4
URL:            https://xorg.freedesktop.org/
Source0:        https://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.xz
Source1:        https://xorg.freedesktop.org/releases/individual/driver/%{name}-%{version}.tar.xz.sig
Source2:        %{name}.keyring
Patch1:         u_Restore-palette-on-LeaveVT.patch
Patch2:         u_DPMS-Query-DPMS-capabilites-and-query-current-state-before-changing.patch
Patch3:         u_DPMS-Check-for-broken-DPMSGet.patch
Patch4:         u_Refuse-to-run-on-machines-with-simpledrmfb-too.patch
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(fontsproto)
BuildRequires:  pkgconfig(pciaccess) >= 0.10
BuildRequires:  pkgconfig(randrproto)
BuildRequires:  pkgconfig(renderproto)
BuildRequires:  pkgconfig(xextproto)
BuildRequires:  pkgconfig(xorg-macros) >= 1.3
BuildRequires:  pkgconfig(xorg-server) >= 1.6
BuildRequires:  pkgconfig(xproto)
Supplements:    xorg-x11-server
# This was part of the xorg-x11-driver-video package up to version 7.6
Conflicts:      xorg-x11-driver-video <= 7.6
ExcludeArch:    s390 s390x
%{?x11_abi_videodrv_req}

%description
vesa is an Xorg driver for Generic VESA video cards.

It can drive most VESA-compatible video cards, but only makes use of the
basic standard VESA core that is common to these cards. The driver
supports depths 8, 15 16 and 24.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

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
%doc ChangeLog README.md
%dir %{_libdir}/xorg/modules/drivers
%{_libdir}/xorg/modules/drivers/vesa_drv.so
%{_mandir}/man4/vesa.4%{?ext_man}

%changelog
* Sun Dec 18 2022 Dirk Müller <dmueller@suse.com>
- update to 2.6.0:
  * Refuse to run if framebuffer or dri devices are present
  * VESAValidMode: remove duplicate call to VESAGetRec
  * VESADGASetMode: remove unused variable scrnIdx
  * Build xz tarballs instead of bzip2
* Sat May 14 2022 Stefan Dirsch <sndirsch@suse.com>
- set SUSE_ZNOW to 0 (boo#1197994)
* Thu Mar 10 2022 tiwai@suse.de
- Refuse vesa driver on the system with simpledrmfb (bsc#1193539):
  u_Refuse-to-run-on-machines-with-simpledrmfb-too.patch
* Tue Apr  6 2021 Dirk Müller <dmueller@suse.com>
- modernize spec file (move license to licensedir)
* Fri Sep 11 2020 Stefan Dirsch <sndirsch@suse.com>
- Update to version 2.5.0
  "This release rolls up a few minor bug fixes since 2.4.0. We now refuse
  to run on machines with UEFI firmware (on Linux only, patches welcome
  for other OSes) since it won't work in the general case and you
  probably have a kernel framebuffer driver running already. We also only
  attempt to use 24bpp if the alternative would be pseudocolor, but note
  that since xserver 1.20 24bpp will not work at all. If you'd like to
  fix that case, please note that it is filed as issue #4:
  https://gitlab.freedesktop.org/xorg/driver/xf86-video-vesa/-/issues/4
  We also notice several cases of running on emulated GPUs, in which case
  the shadow framebuffer is disabled by default to improve performance by
  reducing the number of copies.
  All users are recommended to upgrade, ideally to a better video card
  and/or driver."
* Fri Feb 16 2018 sndirsch@suse.com
- Update to version 2.4.0
  * Nothing terribly exciting, but enough bug fixes to justify a
    release.
- supersedes u_Enable-DefaultRefresh-by-default.patch
* Mon May 29 2017 sndirsch@suse.com
- includes everything needed for missing sle issue entries:
  fate #315643-315645, 319159-319161, 319618 (bsc#1041379)
* Tue Jul  5 2016 eich@suse.com
- u_DPMS-Check-for-broken-DPMSGet.patch
  Check for broken DPMSGet (bsc#986974).
* Sun Sep 27 2015 mpluskal@suse.com
- Add gpg signature
* Fri Sep 25 2015 eich@suse.com
- u_DPMS-Query-DPMS-capabilites-and-query-current-state-before-changing.patch
  If the Xserver provides the VBEDPMSGetCapabilities() and VBEDPMSGet()
  API, check DPMS capabilities if a requested DPMS mode is supported before
  changing, and only change DPMS mode when the new state is different from
  the old (bsc#947356, boo#947493).
* Thu Jun 18 2015 zaitor@opensuse.org
- Update to version 2.3.4:
  + configure: Drop PanelID test.
  + Don't include deprecated xf86PciInfo.h.
  + Raise required version of xorg-server to >= 1.6.
* Thu May 22 2014 eich@suse.com
- u_Restore-palette-on-LeaveVT.patch:
  Restore the Palette on LeaveVT - as it is done on CloseScreen() already
  (bnc#719866).
- u_Enable-DefaultRefresh-by-default.patch:
  Update comments.
* Tue Sep 10 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 2.3.3:
  A few cleanups, and a build fix for xserver 1.14.
  + Remove Upstreamed Patch1: U_mibstore.patch
  + Adapt Patch0: u_Enable-DefaultRefresh-by-default.patch (formerly
    known as xf86-video-vesa_DefaultRefresh.diff) to work with
    version 2.3.3
* Wed Aug  7 2013 ro@suse.de
- add ExcludeArch for s390 and s390x
* Tue Mar 19 2013 hrvoje.senjan@gmail.com
- Add mibstore.patch, fixes build with xorg-server 1.14
* Sun Sep  2 2012 zaitor@opensuse.org
- Update to version 2.3.2:
  + Add api 13 compat layer.
  + Convert to new screen conversion APIs.
  + Add missing compat-api header.
* Thu Apr 19 2012 dimstar@opensuse.org
- Update to version 2.3.1:
  + Require a newer version of libpciaccess
  + Code style cleanup to make the map and unmap blocks more
    consistent
  + Build fix for ABI Version 12
  + Be forgiving of character-cell size mismatches in mode sizes
  + Fix memory leak in mode validation
  + Refuse to load if there's a kernel driver bound to the device
- Use %%x11_abi_videodrv_req instead of static VIDEODRV_ABI requires
* Wed Apr 18 2012 vuntz@opensuse.org
- Split xf86-video-vesa from xorg-x11-driver-video.
  Initial version: 2.3.0.
