#global gitdate 20151027
# temporary build fix:
%define _python_bytecompile_build 0

%bcond_with debug
%bcond_without xfake
%define enable_builddocs	0

# Need this for shared objects that reference X Server, or other modules symbols
%define _disable_ld_no_undefined 1

# Alternatives priority for standard libglx.so and mesa libs
%define priority 500

%define rel 5

%global __provides_exclude_from %{_datadir}/%{name}-source
%global __requires_exclude_from %{_datadir}/%{name}-source

# Released ABI versions.  Have to keep these manually in sync with the
# source because rpm is a terrible language.
%global ansic_major 0
%global ansic_minor 4
%global videodrv_major 23
%global videodrv_minor 0
%global xinput_major 24
%global xinput_minor 1
%global extension_major 10
%global extension_minor 0

%global pkgname xorg-server

Name: x11-server
Version: 1.19.6
Release:   %mkrel %rel%{?gitdate:.%{gitdate}}
Summary:  X11 servers
Group: System/X11
URL: http://xorg.freedesktop.org
%if 0%{?gitdate}
Source0:   xorg-server-%{gitdate}.tar.xz
%else
Source0:   http://www.x.org/pub/individual/xserver/%{pkgname}-%{version}.tar.bz2
Source1:   gitignore
%endif
Source4:   10-quirks.conf
Source5: mageia-setup-keyboard-udev
Source6: 61-x11-input.rules
Source10: xserver.pamd
# from RH/FC:
# "useful" xvfb-run script
Source20:  http://svn.exactcode.de/t2/trunk/package/xorg/xorg-server/xvfb-run.sh
Source21:  http://svn.exactcode.de/t2/trunk/package/xorg/xorg-server/xvfb-run.1
# for requires generation in drivers
Source30:  xserver-sdk-abi-requires.release
# for finding & loading nvidia and flgrx drivers:
Source90: 00-modules.conf
License: GPLv2+ and MIT

# Instructions to setup your repository clone
# git://anongit.freedesktop.org/git/xorg/xserver
# git checkout origin/server-1.7-branch
# git checkout -b mdv-1.7-cherry-picks
# git am ../03??-*.patch
# git checkout -b mdv-1.7-redhat
# git am ../04??-*.patch
# git checkout -b mdv-1.7-patches
# git am ../09??-*.patch

# Sync with server-1.19-branch
# git format-patch --start-number 100 xorg-server-1.19.0..server-1.19-branch
Patch100: 0100-glx-do-not-pick-sRGB-config-for-32-bit-RGBA-visual.patch
Patch101: 0101-xfree86-add-default-modes-for-16-9-and-16-10.patch

# Fedora Patches

# Various fixes pending upstream
Patch2: 0005-xfree86-Remove-redundant-ServerIsNotSeat0-check-from.patch
Patch3: 0006-xfree86-Make-adding-unclaimed-devices-as-GPU-devices.patch
Patch4: 0007-xfree86-Try-harder-to-find-atleast-1-non-GPU-Screen.patch

# Patches for better integration with the nvidia driver, pending upstream
Patch11: 0001-xfree86-Free-devlist-returned-by-xf86MatchDevice.patch
Patch12: 0002-xfree86-Make-OutputClassMatches-take-a-xf86_platform.patch
Patch13: 0003-xfree86-Add-options-support-for-OutputClass-Options.patch
Patch14: 0004-xfree86-xf86platformProbe-split-finding-pci-info-and.patch
Patch15: 0005-xfree86-Allow-overriding-primary-GPU-detection-from-.patch
Patch16: 0006-xfree86-Add-ModulePath-support-for-OutputClass-confi.patch

# Backport tablet support for Xwayland - *NOT* in server-1.19-branch
Patch9901: 0001-xwayland-Depend-on-wayland-protocols-to-build-tablet.patch
Patch9902: 0002-xwayland-Bind-to-wp_tablet_manager-if-available-and-.patch
Patch9903: 0003-xwayland-Listen-for-wp_tablet_seat-events.patch
Patch9904: 0004-xwayland-Handle-wp_tablet-events.patch
Patch9905: 0005-xwayland-Handle-tablet_tool-events.patch
Patch9906: 0006-xwayland-handle-button-events-after-motion-events.patch
Patch9907: 0007-xwayland-Refactor-cursor-management-into-xwl_cursor.patch
Patch9908: 0008-xwayland-update-cursor-on-tablet-tools-in-proximity.patch
Patch9909: 0009-xwayland-add-tablet-pad-support.patch
Patch9910: 0010-xwayland-Unconditionally-initialize-lists-in-init_ta.patch
Patch9911: 0011-xwayland-Correct-off-by-one-error-in-tablet-button-n.patch
Patch9912: 0012-xwayland-Implement-tablet_tool_wheel-for-scrolling.patch

# Upstream commit fe46cbe for Xwayland - Not in server-1.19-branch
Patch9950: 0001-xwayland-Give-up-cleanly-on-Wayland-socket-errors.patch
# Upstream commit 60f4646a for Xwayland - Not in xorg-server-1.19.6
Patch9951: 0001-xwayland-Keep-separate-variables-for-pointer-and-tab.patch
# Upstream commit 16fd1847 for Xwayland - Not in xorg-server-1.19.6
Patch9952: 0001-xwayland-avoid-race-condition-on-new-keymap.patch

# Submitted upstream
Patch21: 0001-xf86-dri2-Use-va_gl-as-vdpau_driver-for-Intel-i965-G.patch

#Patch6044: xserver-1.6.99-hush-prerelease-warning.patch

Patch7025: 0001-Always-install-vbe-and-int10-sdk-headers.patch

# Submitted upstream, but not going anywhere
Patch7027: xserver-autobind-hotplug.patch

# because the display-managers are not ready yet, do not upstream
Patch10000: 0001-Fedora-hack-Make-the-suid-root-wrapper-always-start-.patch

# Upstream commit a309323328d9d6e0bf
Patch10002: 0001-config-fix-NULL-value-detection-for-ID_INPUT-being-u.patch

# Mageia patches
# git format-patch --start-number 900 mdv-1.6.4-redhat..mdv-1.6.4-patches
Patch900: 0900-Use-a-X-wrapper-that-uses-pam-and-consolehelper-to-g.patch
Patch901: 0901-Don-t-print-information-about-X-Server-being-a-pre-r.patch
Patch902: 0902-Take-width-into-account-when-choosing-default-mode.patch
Patch903: 0903-LED-behavior-fixes.patch
Patch906: 0906-xfree86-need-to-press-Ctrl-Alt-Bksp-twice-to-termina.patch

# Candidates for dropping:
# 902: by pixel, so that X11 choose the best resolution with a better algorithm
# 903: Input subsystem has changed *a lot* since this patch was written... I
#      fear it might break things now
# 906: All this patch does is force users to hit ctrl+alt+bksp twice (with
#      an annoying sound) IF the hotkey is enabled. If the user chooses to
#      enable ctrk+alt+bksp, why force him to hit twice? OTOH, the sound is
#      annoying, and it should teach users to not use ctrl+alt+bksp =D

# Do not crash if Xv is not initialized (patch from xorg-devel ML)
# The crash happened when v4l was loaded and xv was not registered,
# for example on RV610 with radeon driver
Patch4001: 1001-do-not-crash-if-xv-not-initialized.patch

# (cg) Point the user at the journal rather than a logfile at /dev/null
Patch5001: point-user-at-journal-rather-than-dev-null.patch

# from Suse
Patch5009: N_Disable-HW-Cursor-for-cirrus-and-mgag200-kernel-modules.patch
Source5010: u_os-connections-Check-for-stale-FDs.patch

# fix build
Patch23: libglvnd-glx.patch 
Patch24: libglvnd-glamor.patch
Patch25: 35-gcc-10.patch
Patch26: 853.patch

#CVEs
#Patch1000: 0011_CVE-2018-14665_xf86Init_8a59e3b7dbb30532a7c3769c555e00d7c4301170.patch
Patch1000: CVE-2018-14665.patch
Patch1001: 0012_CVE-2020-14345_xkb_f7cd1276bbd4fe3a9700096dec33b52b8440788d.patch
Patch1002: 0013_CVE-2020-14346_Xi_c940cc8b6c0a2983c1ec974f1b3f019795dd4cff.patch
Patch1003: 0014_CVE-2020-14361_xkbSwap_144849ea27230962227e62a943b399e2ab304787.patch
Patch1004: 0015_CVE-2020-14362_record_2902b78535ecc6821cc027351818b28a5c7fdbdc.patch
Patch1005: 0016_CVE-2020-25712_xkb_87c64fc5b0db9f62f4e361444f4b60501ebf67b9.patch
Patch1006: 0017_CVE-2020-14360_xkb_446ff2d3177087b8173fa779fa5b77a2a128988b.patch
Patch1007: 0018_CVE-2021-3472_Xi_7aaf54a1884f71dc363f0b884e57bcb67407a6cd.patch
Patch1008: 0019_CVE-2021-4008_ebce7e2d80e7c80e1dda60f2f0bc886f1106ba60.patch
Patch1009: 0020_CVE-2021-4009_b5196750099ae6ae582e1f46bd0a6dad29550e02.patch
Patch1010: 0021_CVE-2022-2319_xkb_6907b6ea2b4ce949cb07271f5b678d5966d9df42.patch
Patch1011: 0022_CVE-2022-2320_xkb_dd8caf39e9e15d8f302e54045dd08d8ebf1025dc.patch
Patch1012: 0023_CVE-2022-3550_xkb_11beef0b7f1ed290348e45618e5fa0d2bffcb72e.patch
Patch1013: 0024_CVE-2022-3551_xkb_18f91b950e22c2a342a4fbc55e9ddf7534a707d2.patch
Patch1014: 0025_CVE-2022-46340_Xtest_b320ca0ffe4c0c872eeb3a93d9bde21f765c7c63.patch
Patch1015: 0026_CVE-2022-46341_Xi_51eb63b0ee1509c6c6b8922b0e4aa037faa6f78b.patch
Patch1016: 0027_CVE-2022-46342_Xext_b79f32b57cc0c1186b2899bce7cf89f7b325161b.patch
Patch1017: 0028_CVE-2022-46343_Xext_842ca3ccef100ce010d1d8f5f6d6cc1915055900.patch
Patch1018: 0029_CVE-2022-46344_Xi_8f454b793e1f13c99872c15f0eed1d7f3b823fe8.patch
Patch1019: 0030_CVE-2022-4283_xkb_ccdd431cd8f1cabae9d744f0514b6533c438908c.patch
Patch1020: 0031_CVE-2022-3553_Xquartz_dfd057996b26420309c324ec844a5ba6dd07eda3.patch
#Patch1021: 0032_CVE-2023-0494_Xi_0ba6d8c37071131a49790243cdac55392ecf71ec.patch
Patch1021: CVE-2023-0494.patch
Patch1022: 0033_CVE-2023-1393_COW_26ef545b3502f61ca722a7a3373507e88ef64110.patch
Patch1023: 0034_CVE-2023-5367_Xi_541ab2ecd41d4d8689e71855d93e492bc554719a.patch
Patch1024: 0035_CVE-2023-5380_mi_564ccf2ce9616620456102727acb8b0256b7bbd7.patch
Patch1025: 0036_CVE-2023-6377_Xi_0c1a93d319558fe3ab2d94f51d174b4f93810afd.patch
Patch1026: 0037_CVE-2023-6478_randr_14f480010a93ff962fef66a16412fafff81ad632.patch

# Security fixes

%global moduledir	%{_libdir}/xorg/modules
%global sdkdir		%{_includedir}/xorg

%global enable_xorg --enable-xorg

%ifnarch %{ix86} x86_64
%global no_int10 --disable-vbe --disable-int10-module
%endif

%global kdrive --enable-kdrive --enable-xephyr --disable-xfake --enable-xfbdev
%global xservers --enable-xvfb --enable-xnest %{kdrive} %{enable_xorg}

Requires: %{name}-xorg
#Requires: %{name}-xdmx
Requires: %{name}-xnest
Requires: %{name}-xvfb

# This should be removed when any of the vnc packages provide x11-server-xvnc:
Obsoletes: %{name}-xvnc < %{version}-%{release}

%if !%{with xfake}
Obsoletes: %{name}-xfake < %{version}-%{release}
%endif

# temp force new gcc
BuildRequires: gcc >= 5.4.0-2

BuildRequires: git
BuildRequires: libpam-devel
BuildRequires: pkgconfig(dri)
BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(fontutil) >= 1.1
BuildRequires: pkgconfig(gbm)
BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(libudev)
BuildRequires: pkgconfig(pciaccess)
BuildRequires: pkgconfig(pixman-1) >= 0.9.5
BuildRequires: pkgconfig(systemd)
BuildRequires: pkgconfig(xau) >= 1.0.0
BuildRequires: pkgconfig(xaw7) >= 1.0.1
BuildRequires: pkgconfig(xdmcp) >= 1.0.0
BuildRequires: pkgconfig(xext) >= 1.1
BuildRequires: pkgconfig(xfixes)
BuildRequires: pkgconfig(xfont2)
BuildRequires: pkgconfig(xi) >= 1.1.3
BuildRequires: pkgconfig(xkbfile) >= 1.0.4
BuildRequires: pkgconfig(xmu) >= 1.0.0
BuildRequires: pkgconfig(xorg-macros) >= 1.10
BuildRequires: pkgconfig(xpm) >= 3.5.4.2
BuildRequires: pkgconfig(xrender) >= 0.9.4
BuildRequires: pkgconfig(xres) >= 1.0.0
BuildRequires: pkgconfig(xtrans) >= 1.3.5
BuildRequires: pkgconfig(xv)
BuildRequires: x11-proto-devel >= 7.7-11

# for ./hw/xwin/glx/gen_gl_wrappers.py:
%define _python_bytecompile_errors_terminate_build 0

# Probably only needed if we change .l or .y files, but let's have them anyway:
BuildRequires: byacc
BuildRequires: flex

# for xkbcomp patch
BuildRequires: pkgconfig(libcrypto)


BuildRequires: pkgconfig(dbus-1)

#BuildRequires: pkgconfig(dmx)
BuildRequires: pkgconfig(xtst) >= 1.1

BuildRequires: pkgconfig(wayland-client) >= 1.3.0
BuildRequires: pkgconfig(wayland-protocols)
BuildRequires: pkgconfig(epoxy)
BuildRequires: pkgconfig(xshmfence) >= 1.1

BuildRequires: pkgconfig(libunwind)

BuildRequires: pkgconfig(xcb-aux) pkgconfig(xcb-image) pkgconfig(xcb-icccm)
BuildRequires: pkgconfig(xcb-keysyms) pkgconfig(xcb-renderutil)

%if %{enable_builddocs}
BuildRequires: doxygen
BuildRequires: fop
BuildRequires: xmlto
BuildRequires: pkgconfig(xorg-sgml-doctools)
%endif

%description
X.Org X11 X server


%package common
Summary: Xorg server common files
Group: System/X11
License: MIT
Provides: XFree86 = 7.0.0
Requires: rgb
# for 'fixed' and 'cursor' fonts
Requires: x11-font-misc-misc
Requires: x11-font-cursor-misc
Requires: x11-font-alias
Requires: x11-data-xkbdata
Requires: xkbcomp
Requires: udev
# else modesetting fails on minimal install:
Requires: %{mklibname mesaegl 1}
Requires(post): update-alternatives
Requires(postun): update-alternatives
# nvidia-71xx does not support X.org server >= 1.5
Conflicts: x11-driver-video-nvidia71xx < 71.86.09-2
# old fglrx does not support X.org server >= 1.7
Conflicts: x11-driver-video-fglrx < 8.720
# Fix: missing conflicts to allow upgrade from 2008.0 to cooker
# http://qa.mandriva.com/show_bug.cgi?id=36651
Conflicts: x11-driver-video-nvidia-current <= 100.14.19


Provides: xserver-abi(ansic-%{ansic_major}) = %{ansic_minor}
Provides: xserver-abi(videodrv-%{videodrv_major}) = %{videodrv_minor}
Provides: xserver-abi(xinput-%{xinput_major}) = %{xinput_minor}
Provides: xserver-abi(extension-%{extension_major}) = %{extension_minor}
# For proprietary drivers that can support multiple videodrv versions:
Provides: xserver-abi(videodrv) = %{videodrv_major}.%{videodrv_minor}

%description common
X server common files

%package xorg
Summary: Xorg X server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}
Requires: x11-data-xkbdata > 1.3-5
Requires: x11-font-alias
Requires: libx11-common
Recommends: x11-driver-input-libinput

# minimum libxfont needed for xserver-1.9:
Requires: libxfont >= 1.4.2

%rename glamor
%rename x11-driver-video-modesetting

%description xorg
X.org X11 is an open source implementation of the X Window System.  It
provides the basic low level functionality which full fledged
graphical user interfaces (GUIs) such as GNOME and KDE are designed
upon.


%package xnest
Summary: A nested server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}

%description xnest
Xnest is an X server which has been implemented as an ordinary
X application.  It runs in a window just like other X applications,
but it is an X server itself in which you can run other software.  It
is a very useful tool for developers who wish to test their
applications without running them on their real X server.


#%package xdmx
#Summary: Distributed Multihead X Server and utilities
#Group: System/X11
#License: MIT
#Requires: x11-server-common = %{version}-%{release}

#%description xdmx
#Xdmx is a proxy X server that provides multi-head support for multiple displays
#attached to different machines (each of which is running a typical X server).
#When Xinerama is used with Xdmx, the multiple displays on multiple machines
#are presented to the user as a single unified screen.  A simple application
#for Xdmx would be to provide multi-head support using two desktop machines,
#each of which has a single display device attached to it.  A complex
#application for Xdmx would be to unify a 4 by 4 grid of 1280x1024 displays
#(each attached to one of 16 computers) into a unified 5120x4096 display.


%package xvfb
Summary: A X Windows System virtual framebuffer X server
Group: System/X11
# xvfb-run is GPLv2, rest is MIT
License: MIT and GPLv2
Requires: x11-server-common = %{version}-%{release}
Requires: xauth


%description xvfb
Xvfb (X Virtual Frame Buffer) is an X server that is able to run on
machines with no display hardware and no physical input devices.
Xvfb simulates a dumb framebuffer using virtual memory.  Xvfb does
not open any devices, but behaves otherwise as an X display.  Xvfb
is normally used for testing servers.


%package xephyr
Summary: A nested server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}

%description xephyr
Xephyr is an X server which has been implemented as an ordinary
X application.  It runs in a window just like other X applications,
but it is an X server itself in which you can run other software.  It
is a very useful tool for developers who wish to test their
applications without running them on their real X server.  Unlike
Xnest, Xephyr renders to an X image rather than relaying the
X protocol, and therefore supports the newer X extensions like
Render and Composite.


%if %with xfake
%package xfake
Summary: KDrive fake X server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}

%description xfake
KDrive (formerly known as TinyX) is a light-weight X server targetting specific
chipsets. It is recommended to be used on thin-clients and embedded systems.
If you are on a standard desktop system you might want to use x11-server-xorg
and the video driver corresponding to your video card.

This KDrive server is targetted for testing purposes.
%endif

%package xfbdev
Summary: KDrive fbdev X server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}

%description xfbdev
KDrive (formerly known as TinyX) is a light-weight X server targetting specific
chipsets. It is recommended to be used on thin-clients and embedded systems.
If you are on a standard desktop system you might want to use x11-server-xorg
and the video driver corresponding to your video card.

This KDrive server is targetted for being used on top of linux framebuffer.

%package xwayland
Summary: Wayland X Server
Group: System/X11
License: MIT
Requires: x11-server-common = %{version}-%{release}

%description xwayland
Xwayland is an X server for running X clients under Wayland.

%package devel
Summary: SDK for X server driver module development
Group: Development/X11
License: MIT

%define oldxorgnamedevel  %mklibname xorg-x11
Requires: libpixman-1-devel
Requires: libpciaccess-devel
Requires: libxkbfile-devel
Requires: libxext-devel >= 1.1
Requires: pkgconfig(xfont2)
# pkgconfig file needs dri.pc:
Requires: GL-devel

%description devel
The SDK package provides the development files which are necessary for
developing X server driver modules, and for compiling driver modules
outside of the standard X11 source code tree.  Developers writing video
drivers, input drivers, or other X modules should install this package.


%package source
Summary: Xserver source code required to build VNC server (Xvnc)
Group: Development/X11
License: MIT
BuildArch: noarch

%description source
Xserver source code needed to build VNC server (Xvnc)


%prep
%autosetup -N -n %{pkgname}-%{?gitdate:%{gitdate}}%{!?gitdate:%{version}}
rm -rf .git
cp %{SOURCE1} .gitignore
# ick
%global __scm git
%{expand:%__scm_setup_git -q}
%autopatch -p1

# check the ABI in the source against what we expect.
getmajor() {
   grep -i ^#define.ABI.$1_VERSION hw/xfree86/common/xf86Module.h |
   tr '(),' '   ' | awk '{ print $4 }'
}

getminor() {
   grep -i ^#define.ABI.$1_VERSION hw/xfree86/common/xf86Module.h |
   tr '(),' '   ' | awk '{ print $5 }'
}

test `getmajor ansic` == %{ansic_major}
test `getminor ansic` == %{ansic_minor}
test `getmajor videodrv` == %{videodrv_major}
test `getminor videodrv` == %{videodrv_minor}
test `getmajor xinput` == %{xinput_major}
test `getminor xinput` == %{xinput_minor}
test `getmajor extension` == %{extension_major}
test `getminor extension` == %{extension_minor}


%build

%global default_font_path "catalogue:/etc/X11/fontpath.d,built-ins"

%global dri_flags --enable-dri2 --enable-dri3 --enable-suid-wrapper --enable-glamor

%global bodhi_flags --with-vendor-name="%_vendor"

%global wayland --enable-xwayland

%if %with debug
CFLAGS='-DBUILDDEBUG -O0 -g3' \
%endif
autoreconf -f -v --install || exit 1
#--enable-dmx --enable-secure-rpc disabled
%configure %{xservers} \
		--with-log-dir=%{_logdir} \
		--enable-dependency-tracking \
		%{?no_int10} --with-int10=x86emu \
		--with-default-font-path=%{default_font_path} \
		--with-module-dir=%{moduledir} \
		--with-vendor-web="https://bugs.mageia.org" \
		%if %{with debug}
		--enable-debug \
		%else
		--disable-debug \
		%endif
		--with-builderstring="Build ID: %{name} %{version}-%{release}" \
		--with-os-name="$(hostname -s) $(uname -r)" \
		--without-dtrace \
		--disable-xselinux --enable-record --enable-present \
		--enable-config-udev \
		--disable-strict-compilation \
		--enable-dpms \
		--disable-tslib \
		%if %{with xfake}
		--enable-xfake \
		%else
		--disable-xfake \
		%endif
		--disable-install-setuid \
		--enable-pam \
		%{?wayland} \
		%{dri_flags} %{?bodhi_flags} \
		--with-sha1=libcrypto \

pushd include && make xorg-server.h dix-config.h xorg-config.h && popd
%make_build

%install
%make_install moduledir=%{moduledir}

mkdir -p $RPM_BUILD_ROOT%{_libdir}/xorg/modules/{drivers,input}

mkdir -p %{buildroot}%{_sysconfdir}/X11/
ln -s %{_bindir}/Xorg %{buildroot}%{_sysconfdir}/X11/X
ln -sf %{_libexecdir}/Xorg.wrap %{buildroot}%{_bindir}/X

mkdir -p %{buildroot}%{_sysconfdir}/pam.d
install -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xserver
mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps
touch %{buildroot}%{_sysconfdir}/security/console.apps/xserver

mkdir -p $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d

# make sure the (empty) /etc/X11/xorg.conf.d is there, system-setup-keyboard
# relies on it more or less.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
 
mkdir -p %{buildroot}%{_sysconfdir}/X11/app-defaults
mkdir -p %{buildroot}%{_sysconfdir}/X11/fontpath.d

# move README.compiled outside compiled/ dir, so there won't be any problem with x11-data-xkbdata
mv -f %{buildroot}%{_datadir}/X11/xkb/compiled/README.compiled %{buildroot}%{_datadir}/X11/xkb/

# (anssi) manage proprietary drivers
install -d -m755 %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL/standard.conf << EOF
# This file is knowingly empty since the libraries are in standard search
# path. Please do not remove this file.
EOF
touch %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL.conf

mkdir -p %{buildroot}/sbin
mkdir -p %{buildroot}/lib/udev/rules.d/
install -m 0755 %{SOURCE5} %{buildroot}/sbin/mageia-setup-keyboard
install -m 0644 %{SOURCE6} %{buildroot}/lib/udev/rules.d

install -m 755 %{SOURCE30} $RPM_BUILD_ROOT%{_bindir}/xserver-sdk-abi-requires

# Make the source package
%global xserver_source_dir %{_datadir}/x11-server-source
%global inst_srcdir %{buildroot}/%{xserver_source_dir}
mkdir -p %{inst_srcdir}/{Xext,xkb,GL,hw/{xquartz/bundle,xfree86/common}}
mkdir -p %{inst_srcdir}/{hw/dmx/doc,man,doc,hw/dmx/doxygen}
cp {,%{inst_srcdir}/}hw/xquartz/bundle/cpprules.in
cp {,%{inst_srcdir}/}man/Xserver.man
cp {,%{inst_srcdir}/}doc/smartsched
#cp {,%{inst_srcdir}/}hw/dmx/doxygen/doxygen.conf.in
cp {,%{inst_srcdir}/}xserver.ent.in
cp {,%{inst_srcdir}/}hw/xfree86/Xorg.sh.in
cp xkb/README.compiled %{inst_srcdir}/xkb
cp hw/xfree86/xorgconf.cpp %{inst_srcdir}/hw/xfree86

find . -type f | egrep '.*\.(c|h|am|ac|inc|m4|h.in|pc.in|man.pre|pl|txt)$' |
xargs tar cf - | (cd %{inst_srcdir} && tar xf -)
# SLEDGEHAMMER
find %{inst_srcdir}/hw/xfree86 -name \*.c -delete

# Remove unwanted files/dirs
{
    rm -f $RPM_BUILD_ROOT%{_libdir}/X11/Options
    rm -f $RPM_BUILD_ROOT%{_bindir}/in?
    rm -f $RPM_BUILD_ROOT%{_bindir}/ioport
    rm -f $RPM_BUILD_ROOT%{_bindir}/out?
    rm -f $RPM_BUILD_ROOT%{_bindir}/pcitweak
    rm -f $RPM_BUILD_ROOT%{_mandir}/man1/pcitweak.1*
    find $RPM_BUILD_ROOT -type f -name '*.la' | xargs rm -f -- || :
# wtf
%ifnarch %{ix86} x86_64
    rm -f $RPM_BUILD_ROOT%{_libdir}/xorg/modules/lib{int10,vbe}.so
%endif
}
 
install -m 0755 %{SOURCE20} $RPM_BUILD_ROOT%{_bindir}/xvfb-run
install -m 0755 %{SOURCE21} $RPM_BUILD_ROOT%{_mandir}/man1/xvfb-run.1
install -m 0644 %{SOURCE90} $RPM_BUILD_ROOT/usr/share/X11/xorg.conf.d/

%post common
%{_sbindir}/update-alternatives \
	--install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/ld.so.conf.d/GL/standard.conf %{priority}

# (anssi)
%triggerun common -- %{name}-common < 1.3.0.0-17
[ $1 -eq 2 ] || exit 0 # do not run if downgrading
current_glconf="$(readlink -e %{_sysconfdir}/ld.so.conf.d/GL.conf)"
if [ "${current_glconf#*mesa}" == "gl1.conf" ]; then
	# This an upgrade of a system with no proprietary drivers enabled, update
	# the link to point to the new standard.conf instead of libmesagl1.conf (2008.0 change).
	%{_sbindir}/update-alternatives --set gl_conf %{_sysconfdir}/ld.so.conf.d/GL/standard.conf
else
	# XFdrake did not set symlink to manual mode before 2008.0, so we ensure it here.
	%{_sbindir}/update-alternatives --set gl_conf "${current_glconf}"
fi
true

%postun common
if [ ! -f %{_sysconfdir}/ld.so.conf.d/GL/standard.conf ]; then
	/usr/sbin/update-alternatives --remove gl_conf %{_sysconfdir}/ld.so.conf.d/GL/standard.conf
fi

%files

%files common
%dir %{_libdir}/xorg/modules
%dir %{_sysconfdir}/X11
%dir %{_sysconfdir}/X11/app-defaults
%dir %{_sysconfdir}/X11/fontpath.d
%dir %{_sysconfdir}/ld.so.conf.d/GL
%dir %{_sysconfdir}/X11/xorg.conf.d
%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%{_sysconfdir}/ld.so.conf.d/GL/standard.conf
%{_bindir}/gtf
%{_bindir}/cvt
/sbin/mageia-setup-keyboard
/lib/udev/rules.d/61-x11-input.rules
#%{_bindir}/vdltodmx
%{_libdir}/xorg/modules/*
%{_libdir}/xorg/protocol.txt
%{_datadir}/X11/xkb/README.compiled
%{_mandir}/man1/gtf.*
%{_mandir}/man1/cvt.*
#%{_mandir}/man1/vdltodmx.*
%{_mandir}/man4/*

%global Xorgperms %attr(4755, root, root)

%files xorg
%{_bindir}/X
%{_bindir}/Xorg
%{_libexecdir}/Xorg
%{Xorgperms} %{_libexecdir}/Xorg.wrap
%attr(4755,root,root)%{_bindir}/Xwrapper
%{_sysconfdir}/X11/X
%{_sysconfdir}/pam.d/xserver
%{_sysconfdir}/security/console.apps/xserver
%{_mandir}/man1/Xorg.1*
%{_mandir}/man1/Xorg.wrap.1*
%{_mandir}/man1/Xserver.1*
%{_mandir}/man5/Xwrapper.config.5*
%{_mandir}/man5/xorg.conf.5*
%{_mandir}/man5/xorg.conf.d.5*
%{_datadir}/X11/xorg.conf.d/00-modules.conf
%{_datadir}/X11/xorg.conf.d/10-quirks.conf

%files xnest
%{_bindir}/Xnest
%{_mandir}/man1/Xnest.1*

#%files xdmx
#%{_bindir}/Xdmx
#%{_bindir}/dmx*
#%{_bindir}/xdmx*
#%{_mandir}/man1/Xdmx.1*
#%{_mandir}/man1/dmxtodmx.1*
#%{_mandir}/man1/xdmxconfig.1*

%files xvfb
%{_bindir}/Xvfb
%{_bindir}/xvfb-run
%{_mandir}/man1/Xvfb.1*
%{_mandir}/man1/xvfb-run.1*

%files xephyr
%{_bindir}/Xephyr
%{_mandir}/man1/Xephyr.1*

%if %with xfake
%files xfake
%{_bindir}/Xfake
%endif

%files xfbdev
%{_bindir}/Xfbdev

%files xwayland
%{_bindir}/Xwayland

%files devel
%{_bindir}/xserver-sdk-abi-requires
%{_libdir}/pkgconfig/xorg-server.pc
%dir %{_includedir}/xorg
%{sdkdir}/*.h
%{_datadir}/aclocal/xorg-server.m4

%files source
%{xserver_source_dir}
