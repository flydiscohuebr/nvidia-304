%global tarball xf86-input-libinput
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/input

Summary:	Xorg X11 libinput input driver
Name:		x11-driver-input-libinput
Group:		System/X11
Version:	1.1.0
Release:	%mkrel 1
URL:		http://www.github.com/whot/xf86-input-libinput/
License:	MIT

#Source0:    https://github.com/whot/xf86-input-libinput/archive/%{tarball}-%{version}.tar.bz2
Source0:     ftp://ftp.x.org/pub/individual/driver/%{tarball}-%{version}.tar.bz2
Source1:    71-libinput-overrides-wacom.conf

# Fedora-only hack for hidpi screens
# https://bugzilla.redhat.com/show_bug.cgi?id=1413306
Patch01:    0001-Add-a-DPIScaleFactor-option-as-temporary-solution-to.patch

BuildRequires: pkgconfig(libevdev)
BuildRequires: pkgconfig(libinput) >= 0.21
BuildRequires: pkgconfig(udev)
BuildRequires: pkgconfig(xorg-server) >= 1.19.0
BuildRequires: x11-util-macros

Requires: x11-server-common %(xserver-sdk-abi-requires xinput)
Requires: xkeyboard-config
Recommends: libinput-tools

%description
A generic input driver for the X.Org X11 X server based on libinput,
supporting all devices.

%package devel
Summary:	Xorg X11 libinput input driver devel files
Group:		Development/C

%description devel
Xorg X11 libinput input driver development files.

%prep
%autosetup -p 1 -n %{tarball}-%{version}

%build
%configure --disable-static --disable-silent-rules
%make_build

%install
%make_install

cp %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/X11/xorg.conf.d/

%files 
%doc COPYING
%exclude %{_libdir}/xorg/modules/input/libinput_drv.la
%{driverdir}/libinput_drv.so
%{_datadir}/X11/xorg.conf.d/40-libinput.conf
%{_datadir}/X11/xorg.conf.d/71-libinput-overrides-wacom.conf
%{_mandir}/man4/libinput.4*

%files devel
/usr/include/xorg/libinput-properties.h
%{_libdir}/pkgconfig/xorg-libinput.pc
