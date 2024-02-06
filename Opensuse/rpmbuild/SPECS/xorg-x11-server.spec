#
# spec file for package xorg-x11-server
#
# Copyright (c) 2018 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


#Compat macro for new _fillupdir macro introduced in Nov 2017
%if ! %{defined _fillupdir}
  %define _fillupdir /var/adm/fillup-templates
%endif

%ifarch s390 s390x
%define have_wayland 0
%else
%define pci_ids_dir %{_sysconfdir}/X11/xorg_pci_ids
%if 0%{?suse_version} >= 1330 || 0%{?build_xwayland}
%define have_wayland 1
%endif
%endif

%define build_suid_wrapper 0

%if 0%{!?build_suid_wrapper:1}
%ifarch s390 s390x
%define build_suid_wrapper 0
%else
%if 0%{?suse_version} >= 1330
%define build_suid_wrapper 1
%define suid_wrapper_dir %{_libexecdir}
%else
%define build_suid_wrapper 0
%endif
%endif
%endif

Name:           xorg-x11-server
Version:        1.19.7
Release:        lp154.7.14.1
Url:            http://xorg.freedesktop.org/
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

Summary:        X
# Source URL: http://xorg.freedesktop.org/archive/individual/xserver/
License:        MIT
Group:          System/X11/Servers/XF86_4
Source0:        xorg-server-%{version}.tar.bz2
Source1:        sysconfig.displaymanager.template
Source2:        README.updates
Source3:        xorgcfg.tar.bz2
Source4:        xorg-backtrace
Source5:        50-extensions.conf
Source6:        modesetting.ids
Source7:        xorg-tmpfiles.conf
# RPM Macros to be installed. The ABI Versions will be injected by configure.
Source90:       xorg-x11-server.macros.in
# Source91 and Source99 are used to ensure proper ABI provides.
Source91:       xorg-server-provides
Source92:       pre_checkin.sh

BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(bigreqsproto) >= 1.1.0
BuildRequires:  pkgconfig(compositeproto)
BuildRequires:  pkgconfig(damageproto) >= 1.1
BuildRequires:  pkgconfig(dbus-1) >= 1.0
BuildRequires:  pkgconfig(dmx) >= 1.0.99.1
BuildRequires:  pkgconfig(dri) >= 7.8.0
BuildRequires:  pkgconfig(dri2proto)
BuildRequires:  pkgconfig(dri3proto)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(epoxy) >= 1.1
%if 0%{?have_wayland} == 1
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
%endif
BuildRequires:  pkgconfig(fixesproto) >= 4.1
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(fontenc)
BuildRequires:  pkgconfig(fontsproto)
BuildRequires:  pkgconfig(fontutil)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glproto)
BuildRequires:  pkgconfig(ice)
BuildRequires:  pkgconfig(inputproto) >= 1.9.99.902
BuildRequires:  pkgconfig(kbproto) >= 1.0.3
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(pciaccess) >= 0.8.0
BuildRequires:  pkgconfig(pixman-1) >= 0.24
BuildRequires:  pkgconfig(presentproto)
BuildRequires:  pkgconfig(randrproto) >= 1.5.0
BuildRequires:  pkgconfig(renderproto) >= 0.11
BuildRequires:  pkgconfig(resourceproto)
BuildRequires:  pkgconfig(scrnsaverproto)
BuildRequires:  pkgconfig(sm)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xau)
BuildRequires:  pkgconfig(xaw7)
BuildRequires:  pkgconfig(xcb-aux)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-image)
BuildRequires:  pkgconfig(xcb-keysyms)
BuildRequires:  pkgconfig(xcb-renderutil)
BuildRequires:  pkgconfig(xcmiscproto) >= 1.2.0
BuildRequires:  pkgconfig(xdmcp)
BuildRequires:  pkgconfig(xext) >= 1.0.99.4
BuildRequires:  pkgconfig(xextproto) >= 7.1.99
BuildRequires:  pkgconfig(xf86dgaproto)
BuildRequires:  pkgconfig(xf86driproto)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xfont2)
BuildRequires:  pkgconfig(xi) >= 1.2.99.1
BuildRequires:  pkgconfig(xineramaproto)
BuildRequires:  pkgconfig(xkbfile)
BuildRequires:  pkgconfig(xmu)
BuildRequires:  pkgconfig(xorg-macros)
BuildRequires:  pkgconfig(xp)
BuildRequires:  pkgconfig(xpm)
BuildRequires:  pkgconfig(xprintutil)
BuildRequires:  pkgconfig(xproto) >= 7.0.31
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xres)
BuildRequires:  pkgconfig(xshmfence)
BuildRequires:  pkgconfig(xt)
BuildRequires:  pkgconfig(xtrans) >= 1.3.1
BuildRequires:  pkgconfig(xtst) >= 1.0.99.2
BuildRequires:  pkgconfig(xv)
### udev support (broken on openSUSE 11.2, see also bnc #589997)
%if 0%{?suse_version} >= 1130
BuildRequires:  pkgconfig(libudev) >= 143
%endif

%ifnarch s390 s390x
Requires(pre):  %fillup_prereq
%endif
Requires:       pkgconfig
Requires:       xkbcomp
Recommends:     xorg-x11-fonts-core
%ifnarch s390 s390x
Requires:       libpixman-1-0 >= 0.24
%(cat %{SOURCE91})
%endif
Requires:       Mesa
%if 0%{?suse_version} >= 1315
Requires(post):   update-alternatives
Requires(postun): update-alternatives
%endif
Provides:       xorg-x11-Xvfb
Provides:       xorg-x11-server-Xvfb
Provides:       xorg-x11-server-glx
Obsoletes:      xorg-x11-Xvfb
Obsoletes:      xorg-x11-server-glx

Provides:       glamor = %{version}
Provides:       glamor-egl = %{version}
Obsoletes:      glamor < %{version}
Obsoletes:      glamor < 7.6_%{version}
Obsoletes:      glamor-egl < %{version}
Obsoletes:      glamor-egl < 7.6_%{version}

Provides:       xf86-video-modesetting = %{version}
Obsoletes:      xf86-video-modesetting < %{version}
Obsoletes:      xf86-video-modesetting < 7.6_%{version}

Provides:       xorg-x11-server = 7.6_%{version}
Obsoletes:      xorg-x11-server < 7.6_%{version}

 # Remove (also from depending driver(s)) when updating X11_ABI_VIDEODRV by updating the server package - NOTE: also remove from xorg-x11-server.macros.in !
Provides:       X11_ABI_HAS_DPMS_GET_CAPABILITIES

# Xvfb requires keyboard files as well (bnc#797124)
Requires:       xkeyboard-config

# PATCH-FEATURE-OPENSUSE n_xorg-x11-server-rpmmacros.patch dimstar@opensuse.org -- Provide RPM macros to require correct ABI Versions.
Patch1:         nvidia-add-modulepath-support.patch
Patch2:         xserver-autobind-hotplug.patch
Patch3:         xext-shm-downgrade-from-error-to-debug.patch
Patch4:         libglvnd-glx.patch
Patch6:         libglvnd-glamor.patch
Patch7:         35-gcc-10.patch
Patch8:         gcc-12.patch
Patch9:          0011_CVE-2018-14665_xf86Init_8a59e3b7dbb30532a7c3769c555e00d7c4301170.patch
Patch10:         0012_CVE-2020-14345_xkb_f7cd1276bbd4fe3a9700096dec33b52b8440788d.patch
Patch11:         0013_CVE-2020-14346_Xi_c940cc8b6c0a2983c1ec974f1b3f019795dd4cff.patch
Patch12:         0014_CVE-2020-14361_xkbSwap_144849ea27230962227e62a943b399e2ab304787.patch
Patch13:         0015_CVE-2020-14362_record_2902b78535ecc6821cc027351818b28a5c7fdbdc.patch
Patch14:         0016_CVE-2020-25712_xkb_87c64fc5b0db9f62f4e361444f4b60501ebf67b9.patch
Patch15:         0017_CVE-2020-14360_xkb_446ff2d3177087b8173fa779fa5b77a2a128988b.patch
Patch16:         0018_CVE-2021-3472_Xi_7aaf54a1884f71dc363f0b884e57bcb67407a6cd.patch
Patch17:         0019_CVE-2021-4008_ebce7e2d80e7c80e1dda60f2f0bc886f1106ba60.patch
Patch18:         0020_CVE-2021-4009_b5196750099ae6ae582e1f46bd0a6dad29550e02.patch
Patch19:         0021_CVE-2022-2319_xkb_6907b6ea2b4ce949cb07271f5b678d5966d9df42.patch
Patch20:         0022_CVE-2022-2320_xkb_dd8caf39e9e15d8f302e54045dd08d8ebf1025dc.patch
Patch21:         0023_CVE-2022-3550_xkb_11beef0b7f1ed290348e45618e5fa0d2bffcb72e.patch
Patch22:         0024_CVE-2022-3551_xkb_18f91b950e22c2a342a4fbc55e9ddf7534a707d2.patch
Patch23:         0025_CVE-2022-46340_Xtest_b320ca0ffe4c0c872eeb3a93d9bde21f765c7c63.patch
Patch24:         0026_CVE-2022-46341_Xi_51eb63b0ee1509c6c6b8922b0e4aa037faa6f78b.patch
Patch25:         0027_CVE-2022-46342_Xext_b79f32b57cc0c1186b2899bce7cf89f7b325161b.patch
Patch26:         0028_CVE-2022-46343_Xext_842ca3ccef100ce010d1d8f5f6d6cc1915055900.patch
Patch27:         0029_CVE-2022-46344_Xi_8f454b793e1f13c99872c15f0eed1d7f3b823fe8.patch
Patch28:         0030_CVE-2022-4283_xkb_ccdd431cd8f1cabae9d744f0514b6533c438908c.patch
Patch29:         0031_CVE-2022-3553_Xquartz_dfd057996b26420309c324ec844a5ba6dd07eda3.patch
Patch30:         CVE-2023-0494.patch
Patch31:         0033_CVE-2023-1393_COW_26ef545b3502f61ca722a7a3373507e88ef64110.patch
Patch32:         0034_CVE-2023-5367_Xi_541ab2ecd41d4d8689e71855d93e492bc554719a.patch
Patch33:         0035_CVE-2023-5380_mi_564ccf2ce9616620456102727acb8b0256b7bbd7.patch
Patch34:         0036_CVE-2023-6377_Xi_0c1a93d319558fe3ab2d94f51d174b4f93810afd.patch
Patch35:         0037_CVE-2023-6478_randr_14f480010a93ff962fef66a16412fafff81ad632.patch
Patch36:         0038_CVE-2023-6816_dix_9e2ecb2af8302dedc49cb6a63ebe063c58a9e7e3.patch
Patch37:         0039_CVE-2024-0229_dix_ece23be888a93b741aa1209d1dbf64636109d6a5.patch
Patch38:         0040_CVE-2024-0229_dix_219c54b8a3337456ce5270ded6a67bcde53553d5.patch
Patch39:         0041_CVE-2024-0229_Xi_df3c65706eb169d5938df0052059f3e0d5981b74.patch
Patch40:         0042_CVE-2024-0408_glx_e5e8586a12a3ec915673edffa10dc8fe5e15dac3.patch
Patch41:         0043_CVE-2024-0409_ephyr_wayland_2ef0f1116c65d5cb06d7b6d83f8a1aea702c94f7.patch
Patch42:         0044_CVE-2024-21885_Xi_4a5e9b1895627d40d26045bd0b7ef3dce503cbd1.patch
Patch43:         0045_CVE-2024-21886_Xi_bc1fdbe46559dd947674375946bbef54dd0ce36b.patch
Patch44:         0046_CVE-2024-21886_dix_26769aa71fcbe0a8403b7fb13b7c9010cc07c3a8.patch
Patch45:         dix_8b75ec34dfbe435cd3a17e64138e22a37395a6d8.patch
Patch46:         454b3a826edb5fc6d0fea3a9cfd1a5e8fc568747.patch


%description
This package contains the X.Org Server.

%package extra
Summary:        Additional Xservers (Xdmx, Xephyr, Xnest)
Group:          System/X11/Servers/XF86_4
Requires:       Mesa
Requires:       xkbcomp
Requires:       xkeyboard-config
Recommends:     xorg-x11-fonts-core
Provides:       xorg-x11-Xnest
Obsoletes:      xorg-x11-Xnest

%description extra
This package contains additional Xservers (Xdmx, Xephyr, Xnest).

%if 0%{?have_wayland} == 1
%package wayland
Summary:        Xwayland Xserver
Group:          System/X11/Servers/XF86_4
Requires:       xkbcomp
Requires:       xkeyboard-config
Recommends:     xorg-x11-fonts-core

%description wayland
This package contains the Xserver running on the Wayland Display Server.
%endif

%if 0%{?build_suid_wrapper} == 1
%package wrapper
Summary:        Xserver SUID Wrapper
Group:          System/X11/Servers/XF86_4
PreReq:         permissions
Requires:       xorg-x11-server == %{version}
Provides:       xorg-x11-server-wayland = 7.6_%{version}
Obsoletes:      xorg-x11-server-wayland < 7.6_%{version}

%description wrapper
This package contains an SUID wrapper for the Xserver.
%endif

%package sdk
Summary:        X
Group:          System/Libraries
Requires:       autoconf
Requires:       automake
Requires:       c_compiler
Requires:       libtool
Requires:       xorg-x11-server
Requires:       pkgconfig(fontconfig)
Requires:       pkgconfig(fontenc)
Requires:       pkgconfig(freetype2)
Requires:       pkgconfig(ice)
Requires:       pkgconfig(libdrm)
Requires:       pkgconfig(libevdev)
Requires:       pkgconfig(libudev)
Requires:       pkgconfig(mtdev)
Requires:       pkgconfig(sm)
Requires:       pkgconfig(x11)
Requires:       pkgconfig(xau)
Requires:       pkgconfig(xdmcp)
Requires:       pkgconfig(xext)
Requires:       pkgconfig(xfixes)
Requires:       pkgconfig(xkbfile)
Requires:       pkgconfig(xmu)
Requires:       pkgconfig(xorg-macros)
Requires:       pkgconfig(xp)
Requires:       pkgconfig(xpm)
Requires:       pkgconfig(xprintutil)
Requires:       pkgconfig(xrender)
Requires:       pkgconfig(xt)
Requires:       pkgconfig(xtrans)
Requires:       pkgconfig(xv)
Provides:       xorg-x11-sdk
Obsoletes:      xorg-x11-sdk
Provides:       glamor-devel = %{version}
Obsoletes:      glamor-devel < %{version}
Obsoletes:      glamor-devel < 7.6_%{version}
Provides:       xorg-x11-server-sdk = 7.6_%{version}
Obsoletes:      xorg-x11-server-sdk < 7.6_%{version}

%description sdk
This package contains the X.Org Server SDK.

%package source
Summary:        Source code of X.Org server
Group:          Development/Sources

%description source
This package contains patched sources of X.Org Server.

%prep
%setup -q -n xorg-server-%{version} -a3
# Early verification if the ABI Defines are correct. Let's not waste build cycles if the Provides are wrong at the end.
sh %{SOURCE92} --verify . %{SOURCE91}

%autopatch -p1

%build
test -e source-file-list || \
    find -L . -type f \! -name '*.orig' \! -path ./source-file-list > \
    source-file-list

autoreconf -fi
%if 0%{?pci_ids_dir:1}
export PCI_TXT_IDS_DIR=%{pci_ids_dir}
%endif
%configure CFLAGS="%{optflags} -fno-strict-aliasing -Wno-error=array-bounds -Wstringop-overflow=0 -fcommon" \
	    --sysconfdir=/etc \
            --enable-xdmcp \
            --enable-xdm-auth-1 \
            --enable-dri \
            --enable-dri2 \
            --enable-dri3 \
            --enable-glamor \
            --enable-dmx \
            --enable-xnest \
            --enable-kdrive \
            --enable-kdrive-evdev \
            --enable-xephyr \
            --disable-xfake \
            --disable-xfbdev \
            --enable-record \
            --enable-xcsecurity \
            --enable-systemd-logind \
            --with-sha1=libcrypto \
            --disable-linux-acpi \
            --disable-linux-apm \
%ifarch s390 s390x
            --disable-xorg \
            --disable-aiglx \
%else
            --enable-xorg \
%if 0%{?suse_version} > 1120
	    --enable-config-udev \
%endif
%endif
%if 0%{?have_wayland} == 1
            --enable-xwayland \
%else
            --disable-xwayland \
%endif
%if 0%{?build_suid_wrapper} == 1
	    --enable-suid-wrapper \
	    --libexecdir=%{suid_wrapper_dir} \
%endif
            --with-log-dir="/var/log" \
            --with-os-name="openSUSE" \
            --with-os-vendor="SUSE LINUX" \
            --with-fontrootdir="/usr/share/fonts" \
            --with-xkb-path="/usr/share/X11/xkb" \
            --with-xkb-output="/var/lib/xkb/compiled" \
	    --with-default-font-path="/usr/share/fonts/misc:unscaled,\
/usr/share/fonts/Type1/,/usr/share/fonts/100dpi:unscaled,\
%if 0%{?suse_version} > 1210
/usr/share/fonts/75dpi:unscaled,/usr/share/fonts/ghostscript/,\
%else
/usr/share/fonts/75dpi:unscaled,/usr/share/fonts/URW/,\
%endif
/usr/share/fonts/cyrillic:unscaled,\
/usr/share/fonts/misc/sgi:unscaled,\
/usr/share/fonts/truetype/,built-ins"
make %{?_smp_mflags}
make -C hw/kdrive %{?_smp_mflags}

%install
%make_install
make -C hw/kdrive install DESTDIR=%{buildroot}
%ifnarch s390 s390x
# remove .la files
find %{buildroot}%{_libdir}/xorg/modules/ -name "*.la" | \
  xargs rm
install -m 644 hw/xfree86/parser/{xf86Parser.h,xf86Optrec.h} \
  %{buildroot}%{_includedir}/xorg
# bnc #632737
chmod u-s %{buildroot}%{_bindir}/Xorg
mkdir -p %{buildroot}%{_localstatedir}/lib/X11
%if 0%{?pci_ids_dir:1}
%__mkdir_p %{buildroot}%{pci_ids_dir}
install -m 644 %{S:6} %{buildroot}%{pci_ids_dir}
%endif
ln -snf ../../../usr/bin/Xorg %{buildroot}%{_localstatedir}/lib/X11/X
ln -snf ../../var/lib/X11/X %{buildroot}%{_bindir}/X
# boo#1120999
mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 644 %{S:7} %{buildroot}%{_tmpfilesdir}/xorg.conf
%if 0%{?suse_version} > 1120
# get rid of evdev config file, since it's meanwhile shipped with
# evdev driver itself (since 2.10.0)
rm -f %{buildroot}/%{_datadir}/X11/xorg.conf.d/10-evdev.conf
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
cp %{buildroot}/%{_datadir}/X11/xorg.conf.d/10-quirks.conf %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
%{__install} -m 644 %{S:5} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
%endif
%if 0%{?suse_version} < 1315
mkdir -p %{buildroot}%{_libdir}/xorg/modules/updates/{fonts,input,linux,drivers,multimedia,extensions}
install -m 644 $RPM_SOURCE_DIR/README.updates %{buildroot}%{_libdir}/xorg/modules/updates
%endif
%else
rm -f %{buildroot}%{_datadir}/aclocal/*.m4
%endif
%ifarch s390 s390x
rm -f %{buildroot}%{_sysconfdir}/X11/10-quirks.conf
mkdir -p %{buildroot}%{_includedir}/xorg
install -m 644 include/list.h \
         %{buildroot}%{_includedir}/xorg
%endif
%ifnarch s390 s390x
mkdir -p %{buildroot}%{_fillupdir}
install -m 644 %_sourcedir/sysconfig.displaymanager.template \
  %{buildroot}%{_fillupdir}/sysconfig.displaymanager-%{name}
%endif
install -m 755 $RPM_SOURCE_DIR/xorg-backtrace %{buildroot}%{_bindir}/xorg-backtrace
cp %{S:90} .
./config.status --file xorg-x11-server.macros
install -D xorg-x11-server.macros %{buildroot}%{_sysconfdir}/rpm/macros.xorg-server
%ifnarch s390 s390x
%if 0%{?suse_version} >= 1315
mkdir -p %{buildroot}%{_libdir}/xorg/modules/extensions/xorg
mv  %{buildroot}%{_libdir}/xorg/modules/extensions/libglx.so \
    %{buildroot}%{_libdir}/xorg/modules/extensions/xorg/xorg-libglx.so
ln -snf %{_sysconfdir}/alternatives/libglx.so %{buildroot}%{_libdir}/xorg/modules/extensions/libglx.so
%endif
%endif

mkdir -p %{buildroot}/usr/src/xserver
xargs cp --parents --target-directory=%{buildroot}/usr/src/xserver < source-file-list

%post
%tmpfiles_create xorg.conf
%ifnarch s390 s390x
%{fillup_only -an displaymanager}
# Move SaX2 generated xorg.conf file to xorg.conf.sle11
#
# Only in very rare cases a static X configuration is still
# required on sle12. And, in some cases the migration from a
# static sle11 X configuration to a static sle12 X configuration
# is not possible at all, e.g. some video and input drivers
# are no longer available on sle12. In short, trying to migrate
# will result in more harm than benefit.
if [ -f etc/X11/xorg.conf -a ! -f etc/X11/xorg.conf.sle11 ]; then
  echo "xorg.conf exists and xorg.conf.sle11 does not"
  if grep -q "SaX generated X11 config file" etc/X11/xorg.conf; then
    echo "move SaX generated xorg.conf to xorg.conf.sle11"
    mv etc/X11/xorg.conf etc/X11/xorg.conf.sle11
    # remove dangling link (bnc#879360, comment#15)
    rm -f etc/X11/XF86Config
    # prevent %postun of NVIDIA/fglrx driver packages from restoring xorg.conf
    # backup or running sax2 as fallback to create a new xorg.conf (bcn#877315)
    rm -f etc/X11/xorg.conf.nvidia-post \
          etc/X11/xorg.conf.fglrx-post
    chmod -x usr/sbin/sax2
  fi
fi
%if 0%{?suse_version} >= 1315
%_sbindir/update-alternatives \
    --force --install %{_libdir}/xorg/modules/extensions/libglx.so libglx.so %{_libdir}/xorg/modules/extensions/xorg/xorg-libglx.so 50
%endif
%endif
exit 0

%ifnarch s390 s390x
%if 0%{?suse_version} >= 1315
%postun
if [ "$1" = 0 ] ; then
   "%_sbindir/update-alternatives" --remove libglx.so %{_libdir}/xorg/modules/extensions/xorg/xorg-libglx.so
fi
%endif
%endif

%if 0%{?build_suid_wrapper} == 1
%post wrapper
%set_permissions %{suid_wrapper_dir}/Xorg.wrap

%verifyscript wrapper
%verify_permissions -e %{suid_wrapper_dir}/Xorg.wrap
%endif

%files
%defattr(-,root,root)
%ifnarch s390 s390x
%if 0%{?suse_version} > 1120
%dir %{_sysconfdir}/X11/xorg.conf.d
%if 0%{?pci_ids_dir:1}
%dir %{pci_ids_dir}
%{pci_ids_dir}/modesetting.ids
%endif
%{_tmpfilesdir}/xorg.conf
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/10-quirks.conf
%config(noreplace) %{_sysconfdir}/X11/xorg.conf.d/50-extensions.conf
%dir %{_datadir}/X11/xorg.conf.d
%{_datadir}/X11/xorg.conf.d/10-*.conf
%endif
%dir %{_localstatedir}/lib/X11
%endif
%dir %{_localstatedir}/lib/xkb
%dir %{_localstatedir}/lib/xkb/compiled
%dir %{_libdir}/xorg
%{_libdir}/xorg/protocol.txt
%{_mandir}/man1/*
%exclude %{_mandir}/man1/Xdmx.1*
%exclude %{_mandir}/man1/Xephyr.1*
%exclude %{_mandir}/man1/Xnest.1*
%{_localstatedir}/lib/xkb/compiled/README.compiled
%ifnarch s390 s390x
%{_bindir}/Xorg
%if 0%{?build_suid_wrapper} == 1
%{suid_wrapper_dir}/Xorg
%endif
%{_bindir}/X

%{_bindir}/cvt
%{_bindir}/gtf
%{_libdir}/xorg/modules/
%{_mandir}/man4/*
%{_mandir}/man5/*
%{_fillupdir}/sysconfig.displaymanager-%{name}
%{_localstatedir}/lib/X11/X
%if 0%{?suse_version} >= 1315
%ghost %{_sysconfdir}/alternatives/libglx.so
%endif
%endif
%{_bindir}/Xvfb
%{_bindir}/xorg-backtrace

%if 0%{?have_wayland} == 1
%files wayland
%{_bindir}/Xwayland
%endif

%if 0%{?build_suid_wrapper} == 1
%files wrapper
%defattr(-,root,root)
%attr(4755,root,root) %{suid_wrapper_dir}/Xorg.wrap
%endif

%files extra
%defattr(-,root,root)
%{_bindir}/Xephyr
%{_bindir}/Xnest
%{_bindir}/Xdmx
%{_bindir}/dmxaddinput
%{_bindir}/dmxaddscreen
%{_bindir}/dmxinfo
%{_bindir}/dmxreconfig
%{_bindir}/dmxresize
%{_bindir}/dmxrminput
%{_bindir}/dmxrmscreen
%{_bindir}/dmxtodmx
%{_bindir}/dmxwininfo
%{_bindir}/vdltodmx
%{_bindir}/xdmxconfig
%{_mandir}/man1/Xdmx.1*
%{_mandir}/man1/Xephyr.1*
%{_mandir}/man1/Xnest.1*

%files sdk
%defattr(-,root,root)
%{_includedir}/xorg/
%ifnarch s390 s390x
%{_libdir}/pkgconfig/*.pc
%{_datadir}/aclocal/*.m4
%endif
%{_sysconfdir}/rpm/macros.xorg-server

%files source
%defattr(-,root,root)
/usr/src/xserver

%changelog
* Thu Mar 14 2019 Stefan Dirsch <sndirsch@suse.com>
- xorg-tmpfiles.conf and appropriate changes in specfile
  * make sure /var/lib/X11/X still symlinks to /usr/bin/Xorg after
    migrating from sle15(-SP0) to sle15-sp1 and doing a rollback
    (boo#1120999)
* Wed Nov 14 2018 msrb@suse.com
- U_dix-window-Use-ConfigureWindow-instead-of-MoveWindow.patch
  * Fix abort triggered by some uses of screensaver. (bsc#1114822)
* Mon Oct 29 2018 sndirsch@suse.com
- U_Disable-logfile-and-modulepath-when-running-with-ele.patch
  * Disable -logfile and -modulepath when running with elevated
    privileges (bsc#1112020, CVE-2018-14665)
* Tue Apr 17 2018 msrb@suse.com
- U_glx-Do-not-call-into-Composite-if-it-is-disabled.patch
  * Fixes crash when GLX is enabled and Composite disabled.
    (bnc#1079607)
* Mon Apr 16 2018 msrb@suse.com
- n_add-dummy-xf86DisableRandR.patch
  * Add dummy xf86DisableRandR to fix linking with drivers that
    still call it. See explanation inside the patch. (bnc#1089601)
* Thu Apr 12 2018 msrb@suse.com
- U_xfree86-Remove-broken-RANDR-disabling-logic-v4.patch
  * Fix crash on initialization when fbdev and modesetting are used
    together. (bnc#1068961)
- u_randr-Do-not-crash-if-slave-screen-does-not-have-pro.patch
  * Fix crash when using randr when fbdev and modesetting are used
    together. (bnc#1068961)
* Tue Mar 27 2018 msrb@suse.com
- Update and re-enable n_xserver-optimus-autoconfig-hack.patch.
  (bnc#1084411)
* Thu Feb 22 2018 fcrozat@suse.com
- U_xwayland-Don-t-process-cursor-warping-without-an-xwl.patch,
  U_xwayland-Give-up-cleanly-on-Wayland-socket-errors.patch,
  U_xwayland-avoid-race-condition-on-new-keymap.patch,
  U_xwayland-remove-dirty-window-unconditionally-on-unre.patch:
  * Various crash and bug fixes in XWayland server (bgo#791383,
    bgo#790502).
* Tue Feb 20 2018 bwiedemann@suse.com
- Add u_xorg-x11-server-reproducible.patch to make build reproducible
  (boo#1047218)
* Fri Feb  9 2018 sndirsch@suse.com
- U_0001-animcur-Use-fixed-size-screen-private.patch,
  U_0002-animcur-Return-the-next-interval-directly-from-the-t.patch,
  U_0003-animcur-Run-the-timer-from-the-device-not-the-screen.patch,
  U_0004-animcur-Fix-transitions-between-animated-cursors.patch
  * There is a bug in version 1.19 of the X.org X server that can
    cause an infinite recursion in the animated cursor code, which
    has been fixed by these patches (boo#1080312)
- supersedes u_cursors-animation.patch (boo#1020061)
* Tue Jan  9 2018 mwilck@suse.com
- Added u_xfree86-add-default-modes-for-16-9-and-16-10.patch (boo#1075249)
  Improve user experience for users with 16:9 or 16:10 screens
* Sun Dec 24 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.6:
  Another collection of fixes from master. There will likely be at east one more
  1.19.x release in 2018.
* Tue Dec 12 2017 msrb@suse.com
- Depend on pkgconfig's gl, egl and gbm instead of Mesa-devel.
  * Those dependencies are what xorg-x11-server really needs.
    Mesa-devel is too general and is a bottleneck in distribution
    build. (bnc#1071297)
* Thu Nov 23 2017 rbrown@suse.com
- Replace references to /var/adm/fillup-templates with new
  %%_fillupdir macro (boo#1069468)
* Tue Nov 14 2017 msrb@suse.com
- u_os-inputthread-Force-unlock-when-stopping-thread.patch
  * Prevent dead lock if terminating while on inactive VT.
    (bnc#1062977)
* Thu Oct 12 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.5:
  One regression fix since 1.19.4, and fixes for CVE-2017-12176 through
  CVE-2017-12187.
* Thu Oct  5 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.4:
  A collection of stability fixes from the development branch, including
  two minor CVEs (CVE-2017-13721, CVE-2017-13723).
- Remove upstream patches:
  + U_Xi-Do-not-try-to-swap-GenericEvent.patch
  + U_Xi-Verify-all-events-in-ProcXSendExtensionEvent.patch
  + U_Xi-Zero-target-buffer-in-SProcXSendExtensionEvent.patch
  + U_dix-Disallow-GenericEvent-in-SendEvent-request.patch
- Adapt patches to work with the new release:
  + u_Use-better-fallbacks-to-generate-cookies-if-arc4rand.patch
* Thu Aug 31 2017 ilya@ilya.pp.ua
- u_cursors-animation.patch fix cursors animation (boo#1020061)
* Fri Jul 14 2017 sndirsch@suse.com
- disable Xwayland for s390x again; it was wrong to enable it;
  there is no Wayland on s390x and will most likely never exist,
  since there is no gfx card on such systems and no gfx emulation
  either (bsc#1047173)
* Thu Jul 13 2017 sndirsch@suse.com
- u_Use-better-fallbacks-to-generate-cookies-if-arc4rand.patch
  If arc4random_buf() is not available for generating cookies:
  * use getentropy(), if available (which was only recently added to
    glibc)
  * use getrandom() via syscall(), if available (there was no glibc
    wrapper for this syscall for a long time)
  * if all else fails, directly read from /dev/urandom as before, but
    employ O_CLOEXEC, do an OsAbort() in case the random data couldn't be
    read to avoid unsecure situations. Don't know if that's too hard a
    measure but it shouldn't actually occur except on maximum number of
    FDs reached
  (bsc#1025084)
* Fri Jul  7 2017 msrb@suse.com
- U_Xi-Do-not-try-to-swap-GenericEvent.patch,
  U_Xi-Verify-all-events-in-ProcXSendExtensionEvent.patch,
  U_Xi-Zero-target-buffer-in-SProcXSendExtensionEvent.patch,
  U_dix-Disallow-GenericEvent-in-SendEvent-request.patch
  * Fix security issues in event handling. (bnc#1035283,
    CVE-2017-10971, CVE-2017-10972)
* Tue Jul  4 2017 sndirsch@suse.com
- enable Xwayland also for s390x (bsc#1047173)
* Sat Jun 10 2017 sndirsch@suse.com
- includes everything needed for additional sle issue entries:
  CVE-2017-2624, bnc#1025029, bnc#1025084, bnc#1025035
* Fri Jun  9 2017 opensuse@dstoecker.de
- update build requirements
* Tue Jun  6 2017 sndirsch@suse.com
- modesetting.ids: no longer hardcode Intel's Skylake, Broxton,
  and Kabylake IDs to modesetting driver; xf86-video-intel is no
  longer installed by default on these, so it will fallback to
  modesetting driver anyway; still you now can easily switch back
  to intel driver by installing xf86-video-intel package
  (boo#1042873)
* Fri Mar 17 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.3:
  A couple more minor fixes, most notably a revert of a page-flipping
  change that regressed some drivers.
- Remove upstreamd patches:
  + u_busfault_sigaction-Only-initialize-pointer-when-matched.patch
* Thu Mar  2 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.2:
  A collection of stability fixes here across glamor, Xwayland, input,
  and Prime support. Also a security fix for CVE-2017-2624, a timing
  attack which can brute-force MIT-MAGIC-COOKIE authentication.
- Remove upstream patches:
  + U_xfree86-Take-the-input-lock-for-xf86RecolorCursor.patch
  + U_xfree86-Take-the-input-lock-for-xf86ScreenCheckHWCursor.patch
  + U_xfree86-Take-the-input-lock-for-xf86TransparentCursor.patch
* Tue Feb 21 2017 denis.kondratenko@suse.com
- U_xfree86-Take-the-input-lock-for-xf86ScreenCheckHWCursor.patch
  * Add the missing input_lock() around the call into the driver's
  UseHWCursor() callback (bnc #1023845).
- U_xfree86-Take-the-input-lock-for-xf86TransparentCursor.patch
  * The new input lock is missing for the xf86TransparentCursor() entry
  point (bnc #1023845).
* Fri Feb 10 2017 sndirsch@suse.com
- U_xfree86-Take-the-input-lock-for-xf86RecolorCursor.patch
  * fixes random crashes in X in multihead mode if one of the
    monitors is vertically oriented (bnc #1023845)
* Fri Feb  3 2017 sndirsch@suse.com
- N_driver-autoconfig.diff:
  No longer try to load "amdgpu" DDX by default for all GPUs with
  ATI vendor ID; this is now handled instead by an "OutputClass"
  section via kernel driver match, which has been added as config
  file to xf86-video-amdgpu driver package (bnc#1023385)
* Thu Jan 26 2017 sndirsch@suse.com
- N_driver-autoconfig.diff:
  FGLRX does not support new x-server. This change fixes bad
  behavior(with empty config) when radeon ddx loads with amdgpu
  kernel module on SI and CIK cards, and x-server cannot start.
  Radeon ddx with radeon kernel module loads without any problem.
* Thu Jan 12 2017 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.19.1:
  First stable 1.19 release, including a few regression fixes.
* Mon Dec 12 2016 fbui@suse.com
- Replace pkgconfig(libsystemd-*) with pkgconfig(libsystemd)
  Nowadays pkgconfig(libsystemd) replaces all libsystemd-* libs, which
  are obsolete.
* Wed Nov 16 2016 tobias.johannes.klausmann@mni.thm.de
- Update to final 1.19.0
* Sat Nov  5 2016 zaitor@opensuse.org
- Exchange xorg-x11-fonts-core Requires for Recommends. The
  corefonts and cursors are not strickly required as long as one
  have a substitute such as Adwaita installed.
* Mon Sep 19 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.18.99.901:
- Remove upstream pachtes:
  + U_glamor-Remove-the-FBO-cache.patch
  + U_kdrive-fix-up-NewInputDeviceRequest-implementation.patch
  + U_kdrive-set-evdev-driver-for-input-devices-automatica.patch
  + U_ephyr-don-t-load-ephyr-input-driver-if-seat-option-i.patch
  + U_kdrive-don-t-let-evdev-driver-overwrite-existing-dev.patch
  + U_ephyr-ignore-Xorg-multiseat-command-line-options.patch
  + U_ephyr-enable-option-sw-cursor-by-default-in-multi-se.patch
  + U_kdrive-introduce-input-hot-plugging-support-for-udev.patch
  + U_kdrive-add-options-to-set-default-XKB-properties.patch
  + U_config-udev-distinguish-between-real-keyboards-and-o.patch
- Disable u_os-connections-Check-for-stale-FDs.patch (not applicable anymore)
- Adapt patches to work with the new release:
  + n_xserver-optimus-autoconfig-hack.patch (disabled for now as it causes
  problems)
- Remove X.org stack version prefix.
  We are already atleast at verion 7.7. Plus we are updating individual
  components anyway. So the stack version is misleading.
* Tue Jul 19 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.18.4:
  Another pile of backports from the devel branch, primarily in glamor,
  xwayland, and the modesetting driver.
- Remove included patches:
  + u_x86emu-include-order.patch
  + U_modesetting-set-driverPrivate-to-NULL-after-closing-fd.patch
- Update patches to reflect upstream changes:
  + U_glamor-Remove-the-FBO-cache.patch
* Tue Jul 19 2016 mstaudt@suse.com
- U_glamor-Remove-the-FBO-cache.patch
  Fixes (bsc#983743) by not keeping >1 GB of VRAM busy.
* Tue May 24 2016 eich@suse.com
- U_modesetting-set-driverPrivate-to-NULL-after-closing-fd.patch:
  modesetting: Avoid crash in FreeRec() by NULLing a pointer which
  may still be used (boo#981268).
* Mon May 16 2016 eich@suse.com
- Replace
  N_Force-swcursor-for-KMS-drivers-without-hw-cursor-sup.patch
  by
  N_Disable-HW-Cursor-for-cirrus-and-mgag200-kernel-modules.patch
  Only disable HW cursor for cirrus and mgag200. This should fix
  a regression introduced by using modesetting for Intel gen9+
  (boo#980124).
* Sun May  8 2016 eich@suse.com
- modesetting.ids:
  Add file for PCI IDs of ASICs which the modesetting rather
  than the native driver should be used for.
  This includes all Intel Gen9+ hardware (boo#978954).
* Mon May  2 2016 sndirsch@suse.com
- removed u_exa-only-draw-valid-trapezoids.patch; no longer needed
  since pixman 0.32.0
* Fri Apr 29 2016 sndirsch@suse.com
- removed no longer needed patch
  u_ad-hoc-fix-for-mmap-s-truncated-offset-parameter-on-.patch, see
  https://lists.x.org/archives/xorg-devel/2016-April/049493.html for
  upstream discussion; obsoleted by upstream patch
  https://cgit.freedesktop.org/xorg/xserver/commit/?id=4962c8c08842d9d3ca66d254b1ce4cacc4fb3756, which is already in xorg-server 1.18.3
* Tue Apr 12 2016 eich@suse.com
- Add permission verification for SUID wrapper
- Disable SUID wrapper per default until reviewed
* Tue Apr 12 2016 eich@suse.com
-  n_Install-Avoid-failure-on-wrapper-installation.patch:
  rename to:
    N_Install-Avoid-failure-on-wrapper-installation.patch
-  u_xorg-wrapper-Drop-supplemental-group-IDs.patch:
  Drop supplementary group privileges.
-  u_xorg-wrapper-build-Build-position-independent-code.patch:
  Build position independent.
* Tue Apr 12 2016 eich@suse.com
- n_Install-Avoid-failure-on-wrapper-installation.patch:
  Fix up build for wrapper.
- Place SUID wrapper into a separate package:
  xorg-x11-server-wrapper
* Thu Apr  7 2016 eich@suse.com
- Set configure option --enable-suid-wrapper for TW:
  This way, the SUID wrapper is built which allows to run the Xserver
  as root even though the the DM instance runs as user. This allows to
  support drivers which require direct HW access.
* Mon Apr  4 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.18.3:
  A few fixes relative to 1.18.2, including one fairly important
  performance fix to the Present extension.
- Remove U_present-Only-requeue-for-next-MSC-after-flip-failure.patch
  The patch is included in this release.
* Thu Mar 31 2016 tobias.johannes.klausmann@mni.thm.de
- Add patch U_present-Only-requeue-for-next-MSC-after-flip-failure.patch
  Fix a hang while using the present extension
  Bugzilla: https://bugs.freedesktop.org/show_bug.cgi?id=94515
    https://bugs.freedesktop.org/show_bug.cgi?id=94596
* Tue Mar 29 2016 eich@suse.com
- Add automake, autoconf, libtool, c_compiler, pkgconfig(xorg-macros),
  pkgconfig(libudev), pkgconfig(libevdev), pkgconfig(mtdev) to Requires:
  of the SDK. This simplifies the build of Xserver modules.
* Tue Mar 22 2016 eich@suse.com
- Add support for a driver specific PCI IDs files supplementing
  what's in xf86VideoPtrToDriverList(). PCI ID lists may be held
  in /etc/X11/xorg_pci_ids (boo#972126).
* Sat Mar 12 2016 tobias.johannes.klausmann@mni.thm.de
- Update version to 1.18.2:
  A big pile of updates in this one. Highlights include:
  * glamor is updated to use OpenGL core profiles if available, which
    should improve memory usage and performance on modern hardware, and got
    some other performance improvements for rpi and other GLES platforms
  * DRI2, DRI3, and Present all received correctness fixes for hangs,
    crashes, and other weirdness
  * Xwayland server has been updated to support the Xv and the
    xf86vidmode extensions for better compatibility, and fixed some bugs
    with output hotplug and pointer updates
  * Xwin saw improvements to window and clipboard management, and a few
    new keyboard layouts
- Remove upstreamed patches:
  + U_kdrive-evdev-update-keyboard-LEDs-22302.patch
* Mon Mar  7 2016 lbsousajr@gmail.com
- Backport upstream patches for Xephyr input hot-plugging /
  single-GPU multi-seat support:
  * U_kdrive-fix-up-NewInputDeviceRequest-implementation.patch
  * U_kdrive-set-evdev-driver-for-input-devices-automatica.patch
  * U_ephyr-don-t-load-ephyr-input-driver-if-seat-option-i.patch
  * U_kdrive-don-t-let-evdev-driver-overwrite-existing-dev.patch
  * U_ephyr-ignore-Xorg-multiseat-command-line-options.patch
  * U_ephyr-enable-option-sw-cursor-by-default-in-multi-se.patch
  * U_kdrive-introduce-input-hot-plugging-support-for-udev.patch
  * U_kdrive-add-options-to-set-default-XKB-properties.patch
  * U_kdrive-evdev-update-keyboard-LEDs-22302.patch
  * U_config-udev-distinguish-between-real-keyboards-and-o.patch
* Fri Mar  4 2016 eich@suse.com
- u_os-connections-Check-for-stale-FDs.patch
  Ignore file descriptor if socket or devices dies.
  This prevents the Xserver to loop at 100%% when
  dbus dies (boo#954433).
* Thu Feb 25 2016 eich@suse.com
- Add 50-extensions.conf
  Disable the DGA extension by default (boo#947695).
* Thu Feb 25 2016 eich@suse.com
- Replaced u_confine_to_shape.diff
  by u_01-Improved-ConfineToShape.patch
  and u_02-DIX-ConfineTo-Don-t-bother-about-the-bounding-box-when-grabbing-a-shaped-window.patch.
* Wed Feb 10 2016 eich@suse.com
- u_pci-primary-Fix-up-primary-PCI-device-detection-for-the-platfrom-bus.patch
  Fix up primary device detection for the platform bus to fix the Xserver
  on older iMacs (boo#835975).
* Tue Feb  9 2016 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.18.1:
  First release in the 1.18 stable branch. Major themes are bugfixes in
  glamor, the modesetting driver, and the Present extension.
  Xwayland users may want to apply the following pair of patches in
  addition to this release:
  https://patchwork.freedesktop.org/patch/72945/raw/
  https://patchwork.freedesktop.org/patch/72951/raw/
  which combined fix an input issue when hotplugging monitors. Both are
  likely to be included in a future release unless testing discovers
  further problems.
- Remove upstreamed patches:
  + ux_xserver_xvfb-randr.patch
  + U_systemd-logind-do-not-rely-on-directed-signals.patch
  + U_kdrive-UnregisterFd-Fix-off-by-one.patch
  + U_modesetting-should-not-reference-gbm-when-it-s-not-d.patch
* Fri Jan 15 2016 eich@suse.com
- u_Panning-Set-panning-state-in-xf86RandR12ScreenSetSize.patch
  Fix panning when configured in xorg.conf* (boo#771521).
* Fri Jan 15 2016 eich@suse.com
- Handle source-file-list in build not prep
- N_xorg-x11-server-rpmmacros.patch:
  Delete: Process xorg-x11-server.macros in install
* Tue Jan 12 2016 fcrozat@suse.com
- U_modesetting-should-not-reference-gbm-when-it-s-not-d.patch: fix
  build when gbm is not defined.
* Mon Jan 11 2016 eich@suse.com
- u_busfault_sigaction-Only-initialize-pointer-when-matched.patch
  Only initialize pointer when matched (boo#961439).
- u_kdrive-UnregisterFd-Fix-off-by-one.patch ->
    U_kdrive-UnregisterFd-Fix-off-by-one.patch
* Sun Jan 10 2016 eich@suse.com
- Add test for defined macro %%build_xwayland
  This can be used to enable the build of Xwayland and the
  package xorg-x11-server-wayland using a macro in projconf
  (boo#960487).
* Fri Jan  8 2016 eich@suse.com
- Split out Xwayland:
  * Build a package xorg-x11-server-wayland
  * Limit build to Factory (boo#960487).
* Sat Jan  2 2016 hrvoje.senjan@gmail.com
- Enable XWayland on Leap also (boo#960487)
* Wed Nov 25 2015 eich@suse.com
- u_kdrive-UnregisterFd-Fix-off-by-one.patch
  * Copy open file table correctly by avoiding an off-by-one error
  (boo#867483).
* Tue Nov 10 2015 sndirsch@suse.com
- Update to version 1.18.0
  - refreshed N_zap_warning_xserver.diff,
    N_Force-swcursor-for-KMS-drivers-without-hw-cursor-sup.patch
  - supersedes u_fbdevhw.diff,
    U_linux-Add-linux_parse_vt_settings-and-linux_get_keep.patch,
    U_linux-Add-a-may_fail-paramter-to-linux_parse_vt_sett.patch,
    U_systemd-logind-Only-use-systemd-logind-integration-t.patch
* Wed Oct 28 2015 sndirsch@suse.com
- Update to version 1.17.4:
  Minor brown-bag release. The important fix here is Martin's
  clientsWritable change which fixes a crash when built against
  xproto 7.0.28.
- supersedes u_0001-os-make-sure-the-clientsWritable-fd_set-is-initializ.patch
* Wed Oct 28 2015 sndirsch@suse.com
- Update to version 1.17.3:
  Various bugfixes across the board.  The most visible changes
  include fixing GLX extension setup under Xwayland and other
  non-Xorg servers (enabling core contexts in more scenarios),
  and various stability fixes to glamor and the Present extension.
- supersededs the following patches:
  * u_randr_allow_rrselectinput_for_providerchange_and_resourcechange_events.patch
  * u_CloseConsole-Don-t-report-FatalError-when-shutting-down.patch
- removed evdev xorg.conf.d snippet since it's meanwhile shipped with
  evdev driver itself (since version 2.10.0)
* Fri Sep 25 2015 eich@suse.com
- u_vesa-Add-VBEDPMSGetCapabilities-VBEDPMSGet.patch
  Add VBEDPMSGetCapabilities() and VBEDPMSGet() functions
  (bsc#947356, boo#947493).
* Thu Jul 30 2015 tiwai@suse.de
- Backport a few upstream fixes for systemd/VT handling (boo#939838):
  U_linux-Add-linux_parse_vt_settings-and-linux_get_keep.patch
  U_linux-Add-a-may_fail-paramter-to-linux_parse_vt_sett.patch
  U_systemd-logind-Only-use-systemd-logind-integration-t.patch
  U_systemd-logind-do-not-rely-on-directed-signals.patch
* Mon Jul 27 2015 eich@suse.com
- Improve conditional enablement of XWayland.
* Fri Jul 17 2015 tobias.johannes.klausmann@mni.thm.de
- Add patch u_0001-os-make-sure-the-clientsWritable-fd_set-is-initializ.patch
  Prevent segmentation faults with more than 256 clients (introduced
  by xproto 7.0.28 increasing the max client count 256 -> 512)
  Fdo Bug: https://bugs.freedesktop.org/show_bug.cgi?id=91316
* Tue Jun 16 2015 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.17.2:
  Pick up a pile of fixes from master. Notable highlights:
  + Fix for CVE-2015-3164 in Xwayland
  + Fix int10 setup for vesa
  + Fix regression in server-interpreted auth
  + Fix fb setup on big-endian CPUs
  + Build fix for for gcc5
- Dropped patches:
  + Patch110: u_connection-avoid-crash-when-CloseWellKnownConnections-gets-called-twice.patch
  + Patch113: u_symbols-Fix-sdksyms.sh-to-cope-with-gcc5.patch
  + Patch116: U_os-XDMCP-options-like-query-etc-should-imply-listen.patch
  + Patch118: U_int10-Fix-error-check-for-pci_device_map_legacy.patch
  + Patch119: U_xwayland-enable-access-control-on-open-socket.patch
  + Patch120: U_os-support-new-implicit-local-user-access-mode.patch
  + Patch121: U_xwayland-default-to-local-user-if-no-xauth-file-given.patch
  + Patch2000: U_systemd-logind-filter-out-non-signal-messages-from.patch
  + Patch2001: U_systemd-logind-dont-second-guess-D-Bus-default-tim.patch
- Changed patches to work with the new version:
  + Patch114: u_ad-hoc-fix-for-mmap-s-truncated-offset-parameter-on-.patch
* Fri Jun 12 2015 msrb@suse.com
- U_os-support-new-implicit-local-user-access-mode.patch,
  U_xwayland-default-to-local-user-if-no-xauth-file-given.patch,
  U_xwayland-enable-access-control-on-open-socket.patch
  * Prevent unauthorized local access. (bnc#934102, CVE-2015-3164)
* Mon Jun  8 2015 antoine.belvire@laposte.net
- Fix GNOME X Session for some hybrid graphics (rh#1209347):
  + add U_systemd-logind-filter-out-non-signal-messages-from.patch
  + add U_systemd-logind-dont-second-guess-D-Bus-default-tim.patch
* Wed Jun  3 2015 msrb@suse.com
- Fix build of s390/s390x (bnc#933503)
* Sat May 30 2015 eich@suse.com
- U_int10-Fix-error-check-for-pci_device_map_legacy.patch
  * int10: Fix error check for pci_device_map_legacy
    pci_device_map_legacy returns 0 on success (bsc#932319).
* Fri Apr 17 2015 normand@linux.vnet.ibm.com
- Add xorg-x11-server-byte-order.patch to correctly set
  X_BYTE_ORDER when compiling tigervnc on ppc64 architecture.
  Related to bnc#926201
* Mon Mar 30 2015 msrb@suse.com
- U_os-XDMCP-options-like-query-etc-should-imply-listen.patch
  * Enable listening on tcp when using -query. (bnc#924914)
* Fri Feb 20 2015 dimstar@opensuse.org
- Enable systemd-logind integration support:
  + Add pkgconfig(libsystemd-logind) and pkgconfig(dbus-1)
    BuildRequires.
  + Pass --enable-systemd-logind to configure.
* Mon Feb 16 2015 sndirsch@suse.com
- u_ad-hoc-fix-for-mmap-s-truncated-offset-parameter-on-.patch
  * ad hoc fix for mmap's truncated offset parameter on 32bit
    (bnc#917385)
- N_Force-swcursor-for-KMS-drivers-without-hw-cursor-sup.patch
  * hwcursor still considered broken in cirrus KMS ((bnc#864141,
    bnc#866152)
* Tue Feb 10 2015 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.17.1:
  Fixes for CVE 2015-0255.
  + xkb: Don't swap XkbSetGeometry data in the input buffer
  + xkb: Check strings length against request size
* Fri Feb  6 2015 eich@suse.com
- u_symbols-Fix-sdksyms.sh-to-cope-with-gcc5.patch
  Fix sdksyms.sh to work with gcc5 (bnc#916580).
* Thu Feb  5 2015 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.17.0:
  + Continued work to strip out stale code and clean up the server.
    Thousands of lines of unnecessary code have disappeared yet again.
  + The modesetting driver has been merged into the server code base,
    simplifying ongoing maintenance by coupling it to the X server
    ABI/API release schedule. This now includes DRI2 support (so that GLX
    works correctly) along with Glamor support (which handles DRI3).
  + Lots of Glamor improvements, including a rewrite of the core protocol
    rendering functions.
- Remove upstream patches:
  + Patch130: U_BellProc-Send-bell-event-on-core-protocol-bell-when-requested.patch
  + Patch131: U_fb-Fix-invalid-bpp-for-24bit-depth-window.patch
  + Patch200: U_kdrive_extend_screen_option_syntax.patch
  + Patch201: U_ephyr_enable_screen_window_placement.patch
  + Patch202: U_ephyr_add_output_option_support.patch
* Thu Feb  5 2015 msrb@suse.com
- Add xorg-x11-server-source package that contains patched xserver
  sources used to build xorg-x11-Xvnc.
* Tue Nov 18 2014 sndirsch@suse.com
- Update to version 1.16.2
  - Fix present_pixmap when using present_notify_msc
  - Fix present_notify to return right away when querying current
    or past msc.Xext/shm: Detach SHM segment after Pixmap is released
  - xkb: ignore floating slave devices when updating from master (#81885)
  - fb: Fix invalid bpp for 24bit depth window
- supersedes U_fb-Fix-invalid-bpp-for-24bit-depth-window.patch
* Mon Nov 10 2014 Led <ledest@gmail.com>
- fix bashism in post script
* Mon Oct 27 2014 sndirsch@suse.com
- XServer looks for dri.pc during configure. dri.pc is currently
  provided by a Mesa devel package, which is pulled in by other
  requirements, but it might be better to explicitly require dri.pc.
* Mon Sep 29 2014 lbsousajr@gmail.com
- Backport upstream patches to enable Xephyr window placement
  via new "-output" option or new "-screen WxH+X+Y" syntax.
  * U_kdrive_extend_screen_option_syntax.patch
  * U_ephyr_enable_screen_window_placement.patch
  * U_ephyr_add_output_option_support.patch
* Sun Sep 21 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.16.1:
  + mieq: Fix a crash regression in mieqProcessDeviceEvent
  + ListenOnOpenFD: Remove Resets since this is intended to be for hotplugging connections
  + XQuartz: Better support turning off "Displays have separate Spaces" on OS X Mavericks
  + glamor: Fix temp picture coordinates in glamor_composite_clipped_region
  + glx/present: Only send GLX_BufferSwapComplete for PresentCompleteKindPixmap
  + xfree86: Fallback to first platform device as primary
  + xfree86: Allow non-PCI devices as primary
  + xwayland: always include drm.xml in tarballs
* Mon Aug 18 2014 tiwai@suse.de
- A better fix for 24bpp graphics problem with cirrus KMS
  (bnc#890599); Adding a new patch:
  U_fb-Fix-invalid-bpp-for-24bit-depth-window.patch
  while obsoleting two patches:
  u_render-Don-t-generate-invalid-pixman-format-when-using-a-24bpp-framebuffer-with-a-32bit-depth-visual.patch
  u_fb-Correctly-implement-CopyArea-when-using-a-window-with-depth-32-and-24bpp.patch
* Fri Aug 15 2014 sndirsch@suse.com
- no longer add /usr/lib[64]/xorg/modules/updates to module path
  (FATE#317822)
* Wed Aug 13 2014 sndirsch@suse.com
- only add /etc/alternatives/libglx.so as ghost on suse >= 1315
* Wed Aug 13 2014 sndirsch@suse.com
- added /etc/alternatives/libglx.so as ghost
- moved libglx-xorg.so to xorg/xorg-libglx.so to avoid messup in case
  anybody runs ldconfig in modules/extensions
* Tue Aug 12 2014 sndirsch@suse.com
- make use of update-alternatives for libglx.so (FATE#317822)
* Thu Aug  7 2014 eich@suse.com
- Change U_ to u_ as these patches are not upstream yet:
  * U_render-Don-t-generate-invalid-pixman-format-when-using-a-24bpp-framebuffer-with-a-32bit-depth-visual.patch
  - -> u_render-Don-t-generate-invalid-pixman-format-when-using-a-24bpp-framebuffer-with-a-32bit-depth-visual.patch
  * U_fb-Correctly-implement-CopyArea-when-using-a-window-with-depth-32-and-24bpp.patch
  - -> u_fb-Correctly-implement-CopyArea-when-using-a-window-with-depth-32-and-24bpp.patch
  (bnc#890599).
* Thu Aug  7 2014 tiwai@suse.de
- Fix corrupted graphics with 24bpp on cirrus KMS (bnc#890599)
  two patches added:
  U_render-Don-t-generate-invalid-pixman-format-when-using-a-24bpp-framebuffer-with-a-32bit-depth-visual.patch
  U_fb-Correctly-implement-CopyArea-when-using-a-window-with-depth-32-and-24bpp.patch
* Tue Aug  5 2014 eich@suse.com
- U_BellProc-Send-bell-event-on-core-protocol-bell-when-requested.patch
  Send XKB bell event on core protocol bell if such an event is requested.
  This allows to override the system beep by a desktop provided sound
  instead of silently ignore it (bnc#890323).
* Thu Jul 17 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.16.0 (final):
  + Glamor integration. This GL-based X acceleration subsystem now
    offers reasonable performance that avoids software fall backs much
    of the time.
  + XWayland. This provides an X server integrated into a Wayland
    window system. It uses Glamor for rendering, and so avoids most of
    the performance problems inherent in window system layering.
  + systemd integration. This provides for systemd-based launching and
    management which improves boot performance and reliability
  + Elimination of thousands of compiler warnings. We've been slowly
    adding more and more compiler flags to the stock X build to warn us
    of unsafe coding practices. Version 1.16 finally addresses the
    enormous list of these warnings.
  + Glamor for Xephyr. This X-on-X implementation now serves as the
    primary development environment for our new 2D acceleration
    subsystem, permitting rapid development and testing on a single
    machine.
  + Non-PCI device support. Many graphics devices are not enumerated
    with the standard PCI APIs; now the X server can auto-detect and
    configure them as it does in more conventional systems.
* Wed Jul  9 2014 sndirsch@suse.com
- update to 1.16RC4
  * non-PCI device support stuff merged
- supersedes u_arch-Fix-image-and-bitmap-byte-order-for-ppc64le.patch
* Thu Jun  5 2014 tobias.johannes.klausmann@mni.thm.de
- Update to 1.16RC3
- Bugfixes all over the place
* Fri May 30 2014 eich@suse.com
- u_render-Cast-color-masks-to-unsigned-long-before-shifting-them.patch:
  Make sure result of shift operation fits into type of variable. This
  fixes finding the correct visual for RENDER with a BGRA framebuffer
  (bnc#876757).
* Wed May 28 2014 sndirsch@suse.com
- %%post:
  * move SaX2 generated xorg.conf file to xorg.conf.sle11
    Only in very rare cases a static X configuration is still
    required on sle12. And, in some cases the migration from a
    static sle11 X configuration to a static sle12 X configuration
    is not possible at all, e.g. some video and input drivers
    are no longer available on sle12. In short, trying to migrate
    will result in more harm than benefit. (bnc#877315)
  * remove dangling link /etc/X11/XF86Config (bnc#879360, comment#15)
  * prevent %%postun of NVIDIA/fglrx driver packages from
    restoring xorg.conf backup or running sax2 as fallback
    to create a new xorg.conf (bcn#877315)
* Sat May 24 2014 eich@suse.com
- Fix crash in abnormal condition (bnc#879666, bnc#879489):
  * u_connection-avoid-crash-when-CloseWellKnownConnections-gets-called-twice.patch
    Fix a crash when CloseWellKnownConnections() gets called twice.
    This can happen if FatalError() is called in the shutdown procedure.
  * u_CloseConsole-Don-t-report-FatalError-when-shutting-down.patch
    Don't call FatalError() on errors in console ioctls when in shutdown.
* Mon May 19 2014 sndirsch@suse.com
- Added n_xserver-optimus-autoconfig-hack.patch for FATE#316410. This
  is a little hack to make the X server autoconfigure the output sinks
  for Optimus laptops.  This lets them automatically use outputs that
  are only wired to a certain GPU. To be removed once our desktop
  tools can configure this easily.
* Tue May 13 2014 tobias.johannes.klausmann@mni.thm.de
- Remove upstreamed patches:
- u_xfree86-allow-fallback-to-PCI-bus-probe-for-non-seat0-seats.patch
  (patch108)
- u_xfree86-add-new-key-MatchSeat-to-xorg-conf.patch (patch109)
- u_xfree86-add-short-description-about-MatchSeat-key-in-xorg-conf-man-page.patch
  (patch110)
* Mon May  5 2014 tobias.johannes.klausmann@mni.thm.de
- Remove N_fix_XWAYLAND_SCANNER_undefined.diff
  Configure line is gone
* Wed Apr 30 2014 lbsousajr@gmail.com
- Add new patches to make non-seat0 X servers work properly with
  non-KMS video drivers:
  + u_xfree86-allow-fallback-to-PCI-bus-probe-for-non-seat0-seats.patch
  + u_xfree86-add-new-key-MatchSeat-to-xorg-conf.patch
  + u_xfree86-add-short-description-about-MatchSeat-key-in-xorg-conf-man-page.patch
* Mon Apr 28 2014 sndirsch@suse.com
- added missing pkgconfig(xf86dgaproto) BuildRequires
* Sun Apr 27 2014 stefan.bruens@rwth-aachen.de
- N_fix_XWAYLAND_SCANNER_undefined.diff
  * handle undefined XWAYLAND_SCANNER_RULES in configure; fix
    compilation for openSUSE 12.3
* Fri Apr 25 2014 tobias.johannes.klausmann@mni.thm.de
- Add missing BuildRequires
* Tue Apr  8 2014 tobias.johannes.klausmann@mni.thm.de
- Update to 1.16RC2
- Build and pack XWayland DDX
* Sat Mar 22 2014 coolo@suse.com
- obsolete glamor-devel from the correct package
* Fri Mar 21 2014 sndirsch@suse.com
- obsolete also glamor and glamor-devel in addition to glamor-egl
* Mon Feb 24 2014 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.16.0pre:
- Remove upstreamed patches:
  + Patch223: U_keep_non_seat0_x_server_from_touching_vts.patch
* Mon Feb 24 2014 eich@suse.com
- u_arch-Fix-image-and-bitmap-byte-order-for-ppc64le.patch:
  arch: Fix image and bitmap byte order for ppc64le (bnc#865069)
* Fri Feb  7 2014 eich@suse.com
- remove creation of libxf86config which was once used bu SaX2.
* Thu Jan 30 2014 lbsousajr@gmail.com
- Rename u_keep_non_seat0_x_server_from_touching_vts.patch to
  U_keep_non_seat0_x_server_from_touching_vts.patch, since it's
  now upstreamed.
  * See: http://cgit.freedesktop.org/xorg/xserver/commit/?id=46cf2a60934076bf568062eb83121ce90b6ff596
* Wed Jan 15 2014 sndirsch@suse.com
- removed N_randr_fix_abi.patch, since it caused the crash with
  current NVIDIA drivers built against xorg-server 1.15 (bnc#858827)
* Tue Jan  7 2014 sndirsch@suse.com
- changed license back to MIT, since xf4nc is no longer patched
  into X.Org sources (bnc#856905)
* Wed Jan  1 2014 crrodriguez@opensuse.org
- Also build with --disable-linux-apm as lnx_apm.lo is still
  built even if --disable-linux-acpi is used.
  Both are obsolete and very likely dangerous to use nowadays.
* Sun Dec 29 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.15.0:
  The final 1.15 release!
* Fri Dec 20 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14.99.905 (1.15 RC5):
  We're getting perilously close to 1.15 now; this should be the last RC
  before we're done next week. If you haven't bothered to test a recent
  candidate, now would be an awesome time to do so and make sure we're
  releasing something that's going to work for you.
* Mon Dec 16 2013 lbsousajr@gmail.com
-  Add u_keep_non_seat0_x_server_from_touching_vts.patch
  * See: http://cgit.freedesktop.org/~jwrdegoede/xserver/commit/?id=405e2805d3903a8a631f01924593a227c634f05d
  * Pull request to main xserver git tree scheduled after 1.15 release
* Thu Dec 12 2013 msrb@suse.com
- u_exa-only-draw-valid-trapezoids.patch
  * Fix possible x server crash using invalid trapezoids.
    (bnc#853846 CVE-2013-6424)
* Thu Dec 12 2013 eich@suse.com
- Changed patch numbering, reordered patches to group
  SUSE specific and to-be-upstreamed patches.
- Added descriptions to a number of patches.
- Renamed some patches:
  * N_p_default-module-path.diff ->
    N_default-module-path.diff
  * n_xorg-x11-server-rpmmacros.patch ->
    N_xorg-x11-server-rpmmacros.patch
* Wed Dec 11 2013 eich@suse.com
- Dropped:
  * N_0001-Check-harder-for-primary-PCI-device.patch
    Whith libpciaccess code path irrelevant for Linux.
  * N_0001-Fix-segfault-when-killing-X-with-ctrl-alt-backspace.patch
    Solved differently upstream
  * N_bug-197858_dpms.diff
    This one is upstream already - apparently nobody check this when
    it no longer applied...
  * N_bug534768-prefer_local_symbols.patch
    Upstream has a better suggestion how to solve this. However this
    patch is no longer needed
  * N_dpms_screensaver.diff
    This topic was solved slightly differently upstream - still patch
    got ported without checking it's context.
  * N_randr1_1-sig11.diff
    No longer needed. Problem was fixed differently upstream.
  * u_vgaHW-no-legacy.patch
    Problem solved in the nv driver.
- Renamed:
  Those patches will go upstream, thus they are prefixed by a u_:
  * n__confine_to_shape.diff ->  u_confine_to_shape.diff
  * N_fbdevhw.diff -> u_fbdevhw.diff
  * n_x86emu-include-order.patch -> u_x86emu-include-order.patch
  * N_xorg-server-xdmcp.patchA -> u_xorg-server-xdmcp.patch
  Those patches no longer apply but are kept for reference thus prefixed by b_:
  * N_0001-Prevent-XSync-Alarms-from-senslessly-calling-CheckTr.patch ->
    b_0001-Prevent-XSync-Alarms-from-senslessly-calling-CheckTr.patch
  * N_cache-xkbcomp-output-for-fast-start-up.patch ->
    b_cache-xkbcomp-output-for-fast-start-up.patch
  * N_sync-fix.patch -> b_sync-fix.patch
  Those patches came from a foreign source but are not upstream, yet, thus
  prefix ux_:
  * u_xserver_xvfb-randr.patch -> ux_xserver_xvfb-randr.patch
* Wed Dec 11 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14.99.904 (1.15 RC4):
  Here's another RC this week. This includes fixes for the GLX regression
  on OS X and Windows, and fixes for Xinerama and various extensions.
- Drop superseded patches:
  + Patch143: n_autoconf-On-Linux-give-fbdev-driver-a-higher-precedence-than-vesa.patch
* Thu Dec  5 2013 sndirsch@suse.com
- removed no longer applied n_Xvnc-pthread.diff from package
* Thu Nov 28 2013 tobias.johannes.klausmann@mni.thm.de
- Update to 1.14.99.903 (1.15 RC3):
- Remove upstreamed patches:
  + Patch228: u_aarch64-support.patch
  + Patch229: u_disable-acpi-code.patch
  A new configure option controls this now
  + Patch240: U_revert_dri2_realloc_dri2_drawable_if-pixmap_serial_changes.patch
  + Patch242: U_randr_dont_directly_set_changed_bits_in_randr_screen.patch
  + Patch243: U_randr_report_changes_when_we_disconnect_a_GPU_slave.patch
  + Patch244: u_randr_send_rrproviderchangenotify_event.patch
  + Patch245: u_randr_send_rrresourcechangenotify_event.patch
  + Patch246: u_randr_deliver_output_and_crtc_events_of_attached_output.patch
  + Patch249: U_xserver_enable_grabdevice_by_default_for_non_seat0.patch
- Drop superseded patches:
  + Patch16:  N_p_xnest-ignore-getimage-errors.diff
  + Patch79:  N_edid_data_sanity_check.diff
* Thu Nov 28 2013 lbsousajr@gmail.com
- Fix naming convention for last patch
* Thu Nov 28 2013 lbsousajr@gmail.com
- Add U_xserver_enable_grabdevice_by_default_for_non_seat0.patch
  * See http://cgit.freedesktop.org/xorg/xserver/commit/?id=c73c36b537f996574628e69681833ea37dec2b6e
* Wed Nov  6 2013 schwab@suse.de
- N_x86emu-include-order.patch: Change include order to avoid conflict
  with system header, remove duplicate definitions
* Fri Nov  1 2013 msrb@suse.com
- N_randr_fix_abi.patch
  * Fixes compatibility with nvidia binary drivers. (bnc#849152)
* Mon Oct 28 2013 sndirsch@suse.com
- Update to prerelease 1.14.4-rc1 (1.14.3.901)
  * bugfixes
  * fixes for security issue CVE-2013-4396
- obsoletes u_Avoid-use-after-free-in-dix-dixfonts.c-doImageText.patch
* Fri Oct 25 2013 msrb@suse.com
- Add U_randr_dont_directly_set_changed_bits_in_randr_screen.patch,
  U_randr_report_changes_when_we_disconnect_a_GPU_slave.patch,
  u_randr_send_rrproviderchangenotify_event.patch,
  u_randr_send_rrresourcechangenotify_event.patch,
  u_randr_deliver_output_and_crtc_events_of_attached_output.patch,
  u_randr_allow_rrselectinput_for_providerchange_and_resourcechange_events.patch
  * Send randr 1.4 events to allow tools to react to new providers. (fate#316408, fate#316409)
* Tue Oct 15 2013 sndirsch@suse.com
- u_Avoid-use-after-free-in-dix-dixfonts.c-doImageText.patch
  * Fixes a security issue, in which an authenticated X client
  can cause an X server to use memory after it was freed,
  potentially leading to crash and/or memory corruption.
  (CVE-2013-4396, bnc#843652)
* Fri Sep 13 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14.3:
  Bugfix release. Changes all over the place.
- Remove upstreamed patches:
  + Patch227: u_init_framebuffer_base.patch
* Tue Sep 10 2013 sndirsch@suse.com
- removed modprobe options for NVIDIA kernel module, since these
  have been moved to the NVIDIA packages themselves
* Fri Aug  9 2013 eich@suse.com
- Delete N_0001-Xinput-Catch-missing-configlayout-when-deleting-dev.patch:
  This patch is no longer appicable. The code has been reworked completely
  thus the problem fixed with this most likely no longer exists.
- Delete N_Use-external-tool-for-creating-backtraces-on-crashes.patch:
  This feature has multiple issues, there is no reason to keep the patch
  around.
* Fri Aug  9 2013 tobias.johannes.klausmann@mni.thm.de
- Remove the unused Xvnc packages
- Remove the now unused vnc macro
- Remove the Xvnc patches:
  + Patch17: n_VNC-Add-support-for-VNC.patch
  + Patch18: n_VNC-Readd-timeout-when-vnc-viewer-connection-breaks.patch
  + Patch19: n_VNC-Fix-crash-when-no-depth-translation-is-required.patch
  + Patch20: n_VNC-Don-t-let-VNC-access-the-framebuffer-directly-an.patch
  + Patch21: n_VNC-Enable-use-of-all-keyboard-layouts-independent-o.patch
  + Patch22: n_VNC-Fix-crash-due-to-unset-input-device-names.patch
  + Patch23: n_Xvnc-pthread.diff
  + Patch24: n_VNC-Add-proto.diff
* Thu Aug  8 2013 eich@suse.com
- n_autoconf-On-Linux-give-fbdev-driver-a-higher-precedence-than-vesa.patch:
  At SUSE we want to perfer the fbdev driver over the VESA driver
  at autoconfiguration as it is expected that fbdev will work in
  allmost all situations where no native driver can be found -
  even under UEFI and with secure boot.
  replaces: N_autoconfig_fallback_fbdev_first.diff
* Thu Aug  8 2013 sndirsch@suse.com
- removed N_vidmode-sig11.diff (fixed upstream already)
* Tue Jul  2 2013 hrvoje.senjan@gmail.com
- Update to version 1.14.2:
  + Bugfix release, changes include:
  + dix: fix device scaling to use a [min,max[ range.
  + dix: pre-scale x by the screen:device:resolution ratio
  + os: Reset input buffer's 'ignoreBytes' field
  + dix: don't overwrite proximity/focus classes
  + dix: plug memory leak in freeing TouchClass
  + os: Use ErrorFSigSafe from FatalError and it's friends
  + dix: send the current axis value in DeviceChangedEvents (fdo#62321)
  + Xi: Use correct destination when swapping barrier events
  + xf86: don't hotplug output devices while VT switched.
* Wed Jun 19 2013 tobias.johannes.klausmann@mni.thm.de
- Packaging changes:
  + Added patch240:
    U_revert_dri2_realloc_dri2_drawable_if-pixmap_serial_changes.patch
    For detailed information visit:
    http://cgit.freedesktop.org/xorg/xserver/commit/?id=77e51d5bbb97eb5c9d9dbff9a7c44d7e53620e68
* Thu Jun  6 2013 msrb@suse.com
- u_xserver_xvfb-randr.patch
  * Add randr support to Xvfb (bnc#823410)
* Sat May 11 2013 schwab@suse.de
- Update u_aarch64-support.patch: disable x86 asm also on aarch64
* Thu Apr 18 2013 sndirsch@suse.com
- u_disable-acpi-code.patch
  * Don't build the ACPI code (bnc#805304)
* Wed Apr 17 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14.1:
  This release contains the fix for CVE-2013-1940, see here for more
  detail: http://lists.x.org/archives/xorg-devel/2013-April/036014.html
  In the remainder we have two build fixes, a couple of comment fixes and a
  change to the list.h code to inline the xorg_list_init function. Fairly
  unintrusive, the lot.
* Fri Apr  5 2013 idonmez@suse.com
- Add Source URL, see https://en.opensuse.org/SourceUrls
* Wed Mar 13 2013 sndirsch@suse.com
- rebased u_aarch64-support.patch and reenabled it
* Fri Mar  8 2013 tobias.johannes.klausmann@mni.thm.de
- u_aarch64-support.patch: Basic support for aarch64 disabled for
  the initial build of 1.14.0!
* Wed Mar  6 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14.0:
  Here's the 1.14 X server release; the last couple of weeks
  yielded a couple of useful bug fixes, but nothing that earth
  shattering.
  + a bunch of fixes to the touch device
  + a few fixes to the GPU hotplug bits
  + software rendering speedups (due to using the new pixman APIs)
  + elimination of a lot of warning messages (we've still too many)
  + pointer barriers work
  There are lots of other fixes too, as always thanks to all who provided
  patches, review and comments for this release!
* Wed Mar  6 2013 schwab@suse.de
- u_aarch64-support.patch: Basic support for aarch64.
* Thu Feb 21 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.14 RC2 1.13.99.902:
  + Remove upstreamed patches:
  u_Do-not-use-intel-driver-on-Poulsbo-Oaktrail-Medfield.patch (patch225)
* Wed Feb 20 2013 sndirsch@suse.com
- added u_init_framebuffer_base.patch: initialize buffer.base to fix
  Xorg segfault in virtualbox guest (bnc#799480)
* Thu Jan 31 2013 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.13.2:
  No commits since rc1.
  Commits from rc1:
  + EnableDisableExtensionError: Use ARRAY_SIZE rather than sentinel
  + glx/dri2: initialise api to avoid indirect rendering failing randomly
  + XQuartz: Avoid a possible deadlock with DRI on OS X 10.7.5 and OS
    X 10.8.2
  + XQuartz: Add some verbose logging to debug xp_lock_window being
    unbalanced
  + XQuartz: Don't add the 15bit visual any more
  + version bump for 1.13.1.901 (rc1)
  + vfb: Initialize the GLX extension again.
* Thu Jan 10 2013 sndirsch@suse.com
- disabled build of VNC (xf4vnc), which finally has been replaced
  by the seperate xorg-x11-Xvnc source package (tigervnc)
* Tue Jan  8 2013 sndirsch@suse.com
- let xorg-x11-server require xkeyboard-config again, since Xvfb
  is part of this package and requires keyboard files as well
  (bnc#797124)
* Fri Dec 14 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.13.1:
- Remove upstreamed patches: (double checked)
  + U_EXA-Track-source-mask-pixmaps-more-explicitly-for-Co.patch
- Removed unrecognized configure options
  + "--enable-builddocs"
* Tue Nov 27 2012 werner@suse.de
- Let the old Xfig program find the ghostscript fonts (bnc#784305)
* Mon Nov 12 2012 fcrozat@suse.com
- Update N_autoconfig_fallback_fbdev_first.diff to ensure
  modesetting driver is used before fbdev.
* Tue Oct 30 2012 sndirsch@suse.com
- U_EXA-Track-source-mask-pixmaps-more-explicitly-for-Co.patch
  Track source/mask pixmaps more explicitly for Composite fallback regions.
  In particular, make sure pExaScr->src/maskPix are cleared when the
  corresponding pictures aren't associated with drawables, i.e. solid or
  gradient pictures. Without this, we would in some cases associate the
  source/mask region with unrelated pixmaps from previous Composite
  fallbacks, resulting in random corruption. (bnc#786153, fdo#47266)
* Mon Oct 15 2012 sndirsch@suse.com
- u_vgaHW-no-legacy.patch
  * likely fixes build on ppc
* Mon Sep 24 2012 opensuse@cboltz.de
- /usr/bin/Xorg is no longer listed in /etc/permissions - remove
  %%set_permissions and %%verify_permissions and re-enable rpm permission
  check (bnc#632737 #c27)
* Thu Sep 20 2012 sndirsch@suse.com
- N_driver-autoconfig.diff
  * "ati" needs to be the second choice right after "fglrx"; there
    must not be a gap between "fglrx" and "ati" introduced by
    removing "radeonhd" from this list by the previous change
* Tue Sep 18 2012 sndirsch@suse.com
- N_driver-autoconfig.diff:
  * removed radeonhd and unichrome from driver list, since no
    longer supported upstream
* Wed Aug  8 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.13.0:
  + Packaging changes:
  - Unify naming of patches
  - Drop upstreamed patches: 223, 224, 300 - 310 (double checked)
  - Remove patch pio_ia64.diff - not applicable anymore
  - Remove patch xserver-bg-none-root.patch - not applicable anymore
  - Remove patch bug474071-fix1.diff - not appliable anymore
  - Remove patch pci-legacy-mem-fallback.diff - not applicable anymore
  - Remove patch pu_fixes.diff - not applicable anymore (xaa is gone)
* Sun Jul 22 2012 sndirsch@suse.com
- u_Do-not-use-intel-driver-on-Poulsbo-Oaktrail-Medfield.patch
  * Do not use intel driver on Poulsbo, Oaktrail, Medfield, CDV.
    IDs stolen from Kernel psb driver. (bnc#772279)
  * obsoletes xorg-detect-psb.patch
* Tue Jul 17 2012 sndirsch@suse.com
- renamed patches of previous change according to our policy
  u_* --> U_* (since these were rebased on upstream patches)
* Fri Jul 13 2012 badshah400@gmail.com
- Add patches u_dri2_add_DRI2CreateDrawable2.patch and
  u_0012-glx_Free_reference_to_destroyed_GLX_drawable.patch to fix
  seemingly random crashes of the X stack [bnc#769553]; patches
  came from upstream git commits, and were rebased to apply to
  present version cleanly.
* Mon Jul  9 2012 tobias.johannes.klausmann@mni.thm.de
- Update to Version 1.12.3
  + The third stable update to the X.Org X server 1.12 series is now available.
    A few smaller changes only since the second RC, some memory leak fixes and two
    fixes to avoid out-of-bounds array access.
* Tue Jun 26 2012 sndirsch@suse.com
- removed redundant buildrequires to xorg-x11 meta package
* Thu Jun 14 2012 sndirsch@suse.com
- change xorg-x11 requires to a requires for xkbcomp (xorg-x11 is
  meanwhile a meta package, which requires any X sample app
  package); background: Xserver uses xkbcomp on startup for
  creating the cache file for xkb keyboard map.
* Fri Jun  8 2012 sndirsch@suse.com
- let xorg-x11-server require Mesa, since that package includes
  the DRI drivers (including the "swrast" DRI driver for software
  rendering), which are required by GLX and AIGLX extensions
  (bnc#765241)
* Wed May 30 2012 tobias.johannes.klausmann@mni.thm.de
- Update to version 1.12.2
* Fri May 25 2012 sndirsch@suse.com
- no longer use obsolete %%run_permissions; replaced it by
  %%set_permissions (bnc#764101)
* Tue May 22 2012 sndirsch@suse.com
- added patches to implement GLX_ARB_create_context extensions
  required for OpenGL 3.0 support (not upstream yet)
* Wed May  9 2012 sndirsch@suse.com
- changed pixman-1-0 requires to version 0.24 (bnc#759537)
* Wed Apr 25 2012 sndirsch@suse.com
- remove BuildRequires to ghostscript-library, since it conflicts
  with ghostscript-mini apparently now required by some other
  package
* Wed Apr 18 2012 mgorse@suse.com
- Rebase VNC patches
  Rebase confine_to_shape.diff
* Sun Apr 15 2012 dimstar@opensuse.org
- Update to version 1.12.1
- Drop xorg-docs-1.6.tar.bz2: the docs are provided in a sep.
  package.
- Add ABI Provides verification:
  + pre_checkin.sh to be launched with --tar before checkin (no
    parameter given will try to do the right thing).
  + pre_checkin.sh is used during build to verify that the ABI
    values match the expectations, to ensure we provide by rpm what
    the binaries do.
- Add rpm macro file, allowing driver and input packages to specify
  %%x11_abi_videodrv_req, %%x11_abi_xinput_req.
- Rebased patches to apply on 1.12.1 code base:
  + 0001-Check-harder-for-primary-PCI-device.patch
  + 0001-Fix-segfault-when-killing-X-with-ctrl-alt-backspace.patch
  + autoconfig_fallback_fbdev_first.diff
  + bug534768-prefer_local_symbols.patch
  + dpms_screensaver.diff
  + driver-autoconfig.diff
  + fbdevhw.diff
  + fix-dpi-values.diff
  + fix_fglrx_screendepth_issue.patch
  + p_default-module-path.diff
  + pu_fixes.diff
  + p_xnest-ignore-getimage-errors.diff
  + randr1_1-sig11.diff
  + vidmode-sig11.diff
  + xorg-detect-psb.patch
  + xorg-server-xdmcp.patch
  + zap_warning_xserver.diff
  + sync-fix.patch
- Drop upstream fixed patches:
  + U_dix-on-PointerRootWin-send-a-FocusIn-to-the-sprite-w.patch
  + U_dix-send-focus-events-to-the-immediate-parent-44079.patch
  + U_Don-t-call-deleted-Block-WakeupHandler.patch
  + u_OS-acpi-Reconnect-to-acpid-when-it-gets-restarted.patch
  + u_record-fix-sig11.patch
* Thu Mar 22 2012 jengelh@medozas.de
- Parallel build with %%_smp_mflags; strip redundant sections/tags
- Use pkgconfig symbols for BuildRequires/Requires
* Tue Feb 28 2012 sndirsch@suse.com
- fixed buildreqs due to reorganization of libvnc/vncproto
* Thu Feb  9 2012 sndirsch@suse.com
- fixed buildreqs due to splitted xorg-x11-libs
* Fri Jan 13 2012 sndirsch@suse.com
- added /usr/share/fonts/misc/sgi to Xserver core font rendering
  fontpath (bnc#738961)
* Tue Jan 10 2012 sndirsch@suse.com
- U_dix-send-focus-events-to-the-immediate-parent-44079.patch/
  U_dix-on-PointerRootWin-send-a-FocusIn-to-the-sprite-w.patch
  * fixed very visible bug in XI2 handling exposed by a gtk+
    bugfix (bnc #740332, fdo #44079)
* Wed Nov 30 2011 ro@suse.de
- also package list.h in s390 so that sax2-tools can build
* Mon Nov 28 2011 ro@suse.de
- complete s390 fixes
* Mon Nov 28 2011 ro@suse.de
- fix build on s390/s390x
* Sun Nov 20 2011 coolo@suse.com
- add libtool as buildrequire to avoid implicit dependency
* Wed Nov  9 2011 sndirsch@suse.com
- u_record-fix-sig11.patch
  * If you aren't using the Record extension (and you aren't), you
    can work around the bug by moving the code which accesses the
    (non-existant) request buffer inside the loop looking at the
    recording contexts (of which there should be none).
    (bnc #728964, fdo #36930)
* Tue Oct 18 2011 eich@suse.com
- U_Don-t-call-deleted-Block-WakeupHandler.patch:
  Don't call deleted Bloxk/WakeupHandler() - this avoids
  crashes when handlers are unregistered from within a handler
  which are in the call chain behind the current handler
  (bnc #723777).
* Tue Oct 18 2011 eich@suse.com
- zap_warning_xserver.diff:
  Fix man page to match changed behavior.
* Tue Sep  6 2011 sndirsch@suse.com
- update to xorg-server 1.10.4
- VNC patches completely redone by Egbert Eich (N-VNC-*)
- Xvnc-pthread.diff: small buildfix required for factory
- removed obsolete patches
  * EXA-mixed-ModifyPixmapHeader-pitch-fixes.-bug-33929.patch
  * Replace-malloc-with-calloc-to-initialize-the-buffers.patch
  * U_xserver_fix-pixmaps-lifetime-tracking.patch
  * commit-5c6a2f9.diff
  * pad-size-of-system-memory-copy-for-1x1-pixmaps
  * record-avoid-crash-when-calling-RecordFlushReplyBuff.patch
  * xorg-server-stop-cpu-eating.diff
- adjusted patches
  * bug534768-prefer_local_symbols.patch
  * zap_warning_xserver.diff
- disabled patches for now
  * 0001-Xinput-Catch-missing-configlayout-when-deleting-dev.patch
  * cache-xkbcomp-output-for-fast-start-up.patch
  * xserver-bg-none-root.patch
  * 0001-Prevent-XSync-Alarms-from-senslessly-calling-CheckTr.patch
-  set VIDEO_ABI_VERSION = 10 and INPUT_ABI_VERSION = 12 in specfile
* Tue Aug 30 2011 sndirsch@suse.com
- U_xserver_fix-pixmaps-lifetime-tracking.patch
  * avoid crash when enabling the desktop icons in gnome3
  (bnc#701199)
* Mon Aug 29 2011 sndirsch@suse.com
- u_xf4nvc_missing-libz.patch
  * Xvnc no longer can rely on the toolchain to add the required
    libs, it uses directly.
* Fri Jul  8 2011 eich@suse.de
- update:
  * randr1_1-sig11.diff
    removed accidentally forgotten debugging code.
  * u_OS-acpi-Reconnect-to-acpid-when-it-gets-restarted.patch
    made socket non-blocking. Idea taken from a pach for SLES11.
* Thu Jul  7 2011 eich@suse.de
- don't look for 10-evdev.conf for anything older than 11.3
  (this includes SLE-11).
* Thu Jul  7 2011 eich@suse.de
- remove use-last-screen.patch:
  This patch has been rejected upstream. We will try to resolve
  this issue differently by not providing any screen, monitor or
  device section.
* Thu Jul  7 2011 eich@suse.de
- remove disable-fbblt-opt.diff:
  We are unable to reproduce this issue any more.
  So let's remove the workaround and start from scratch
  when issue resurfaces and find a proper fix.
* Wed Jul  6 2011 eich@suse.de
- fixed bug-197858_dpms.diff:
  removed pieces that have been solved differently today.
* Wed Jul  6 2011 eich@suse.de
- remove moblin-use_preferred_mode_for_all_outputs.diff:
  remove moblin specific patches.
* Tue Jul  5 2011 eich@suse.de
- rename edit_data_sanity_check.diff -> edid_data_sanity_check.diff
* Tue Jul  5 2011 eich@suse.de
- remove p_xkills_wrong_client.diff:
  made obsolete by commit b7f3618f.
* Tue Jul  5 2011 eich@suse.de
- remove xorg-server-1.8.0.diff:
  issue is now resolved in spec file.
* Tue Jul  5 2011 eich@suse.de
- fix zap_warning_fix.diff:
  recover from noisy people.
* Tue Jul  5 2011 eich@suse.de
- remove p_xorg_acpi.diff
  add u_OS-acpi-Reconnect-to-acpid-when-it-gets-restarted.patch
  removed redundant error message.
* Mon Jul  4 2011 eich@suse.de
- remove mouse.diff:
  Never understood what this patch was good for.
* Mon Jul  4 2011 eich@suse.de
- remove p_bug96328.diff:
  /dev/input/mice is the default mouse for X -configure
  on Linux for a long time already.
* Mon Jul  4 2011 eich@suse.de
- remove xephyr.diff:
  solved by configure options in spec file.
* Mon Jul  4 2011 eich@suse.de
- remove libdrm.diff:
  not needed any more, drivers seem to be fixed.
* Mon Jul  4 2011 eich@suse.de
- remove xorg-docs.diff:
  solved in spec file.
* Mon Jul  4 2011 eich@suse.de
- remove pixman.diff:
  Doesn't seem to be needed any more.
* Mon Jul  4 2011 eich@suse.de
- remove xorg-x11-nonroot-vesa.patch, org-server-nohwaccess.diff:
  There are other things missing to make those patches useful.
* Fri Jul  1 2011 eich@suse.de
- remove: xserver-1.6.1-nouveau.patch.
  This patch was only cosmetic.
* Fri Jul  1 2011 eich@suse.de
- remove: CVE-2010-2240-address_space_limit.patch
    CVE-2010-2240-tree_depth_limit.patch
  These security issues have been handled in the Linux kernel in a
  much more general fashion.
* Fri Jul  1 2011 eich@suse.de
- remove: bitmap_always_unscaled.diff
    missing_font_paths.diff
  This has now been solved in the spec file directly.
* Thu May 26 2011 mhopf@novell.com
- xorg-server-xf4vnc-fix-keyboard-layout-handling.diff
  Consolidate adapted patches for bugs 400520, 605015, and 660797 into
  single patch:
  - xorg-server-xf4vnc-bug660797-fix-keycode-lookup-and-isolevel3shift.diff
  - xorg-server-xf4vnc-bug660797-multilayout.diff
  - xorg-server-xf4vnc-bug605015-fix-keyboard-handling-xinput.diff
- Fix *major* memory leak introduced by original 1.9 enabling patch
* Tue May 24 2011 mhopf@novell.com
- xorg-server-xf4vnc-bug660797-multilayout.diff
  - bnc #605015, 660797, fallout of fix from May 10:
    Keyboard handling was not XKB aware, which lead to a multitude of issues.
    Situation with this patch is not perfect, but way better.
* Thu May 19 2011 mhopf@novell.com
- xorg-server-xf4vnc-bug660797-fix-keycode-lookup-and-isolevel3shift.diff
  - bnc #400520, fallout of previous fix:
    Analysis for shift/level3 event faking was broken, leading to e.g
    Shift+PgUp not being recognized correctly.
* Thu Apr 21 2011 mhopf@novell.com
- bnc #605015
  - Enable use of all keyboard layouts, independent of remotely set layout
  - Remove obsolete xorg-server-xf4vnc-bug605015-vnc-umlauts.diff
  - xorg-server-xf4vnc-bug605015-fix-keyboard-handling-xinput.diff
    This should basically already enable the use of other keyboards, if the
    remote keyboard stays at US.
  - xorg-server-xf4vnc-bug605015-fix-keycode-lookup-and-isolevel3shift.diff
    This patch fixes keycode lookup (not using any static keyboard layout any
    more) and ISO-Level3-Shift handling (enabling the use of keyboard layouts
    that use AltGr for reaching certain characters).
* Tue Apr 12 2011 sndirsch@novell.com
- Xvnc should require xkeyboard-config (bnc #682904)
* Fri Mar 25 2011 sndirsch@novell.com
- EXA-mixed-ModifyPixmapHeader-pitch-fixes.-bug-33929.patch
  * EXA/mixed: ModifyPixmapHeader pitch fixes. (bnc #678264,
    bfo #33929)
* Thu Mar 17 2011 sndirsch@novell.com
- Replace-malloc-with-calloc-to-initialize-the-buffers.patch
  * Replace malloc with calloc to initialize the buffers[] as NULL
    in do_get_buffers function (bnc #673595)
* Thu Mar 17 2011 sndirsch@novell.com
- record-avoid-crash-when-calling-RecordFlushReplyBuff.patch
  * record: avoid crash when calling RecordFlushReplyBuffer
    recursively (bnc #673575)
* Sat Feb 26 2011 devel@navlost.eu
- Added --enable-kdrive-evdev switch to ./configure so that
  the evdev driver can be used with Xephyr's -keybd and -mouse
  switches
* Tue Feb 15 2011 mhopf@novell.com
- Disable Use-external-tool-for-creating-backtraces-on-crashes.patch:
  - Security isn't exactly fond of the patch (bnc#666578)
  - Patch potentially livelocks server in fork() (bnc#660166)
* Fri Feb 11 2011 mhopf@novell.com
- Update xorg-server-xf4vnc-fixes_1_9.diff:
  Fix Xvnc rendering issues.
- Enable build of Xvnc again.
- Merge xorg-server-xf4vnc-fix-crash-on-193.diff
  into xorg-server-xf4vnc-fixes_1_9.diff
* Thu Feb  3 2011 sndirsch@novell.com
- disabled build of Xvnc and moved Xvfb to main package;
  xorg-x11-Xvnc will be a seperate package (bnc #660208)
* Mon Jan 10 2011 vuntz@opensuse.org
- Add xorg-server-stop-cpu-eating.diff to avoid eating 100%% of the
  CPU when auto-detecting which vt to use on startup.
* Wed Jan  5 2011 jeffm@suse.de
- pad-size-of-system-memory-copy-for-1x1-pixmaps:
  * Pad size of system memory copy for 1x1 pixmaps (bnc#652523,
    bfo#32803)
* Mon Jan  3 2011 sndirsch@novell.com
- use-last-screen.patch
  * adjusted the patch to no longer segfault the Xserver during
    startup immediately when there isn't any screen section
    specified at all (bnc #661989)
* Mon Dec 27 2010 sndirsch@novell.com
- use-last-screen.patch
  * Use last Screen section found to prefer xorg.conf (bnc #661536,
    bfo #32430)
* Tue Dec 21 2010 sndirsch@novell.com
- added xorg-server-xf4vnc-bug605015-vnc-umlauts.diff as patch, but
  still disabled
* Tue Dec 21 2010 mhopf@novell.com
- xorg-server-xf4vnc-fix-crash-on-193.diff
  Fix vnc startup crashes (bnc #660208).
  Reenabled build of Xvnc. Massive rendering errors, still.
* Tue Dec 21 2010 sndirsch@novell.com
- bumped version number to 7.6_1.9.3
* Sun Dec 19 2010 sndirsch@novell.com
- sync-fix.patch
  * fixes the issue that gnome screensaver fadeout could not be
    stopped (bnc #648851)
* Sun Dec 19 2010 sndirsch@novell.com
- xorg-docs 1.6
* Mon Dec 13 2010 sndirsch@novell.com
- xorg-server 1.9.3
  * This version is functionally equivalent to the second release
    candidate.
* Sat Dec  4 2010 sndirsch@novell.com
- xorg-server 1.9.2.902 (1.9.3 RC2)
  * includes various build and bug fixes to stability and
    correctness over previous releases
* Fri Dec  3 2010 sndirsch@novell.com
- remove Xorg setuid bit (bnc #632737)
* Sun Nov 14 2010 sndirsch@novell.com
- xorg-server 1.9.2.901 (1.9.3 RC1)
  * many buildfixes and bugfixes
* Fri Nov 12 2010 sndirsch@novell.com
- xorg-docs 1.5.99.901 (1.6 RC1)
- adjusted xorg-x11-doc.diff
* Fri Nov 12 2010 sndirsch@novell.com
- xorg-docs-1.5
- adjusted xorg-docs.diff
* Tue Nov  9 2010 sndirsch@novell.com
- disabled again vnc build due to immediate assertion during
  startup of Xvnc
* Tue Nov  9 2010 sndirsch@novell.com
- uncommented non-existing
  xorg-server-xf4vnc-bug605015-vnc-umlauts.diff
* Tue Nov  9 2010 mhopf@novell.com
- xorg-server-xf4vnc-fixes_1_9.diff:
  Fix build of vnc server for 1.9 Xserver series.
* Mon Nov  1 2010 sndirsch@novell.com
- xorg-server 1.9.2
  * This is a brown-bag release to address an issue with the
    xorg-server-1.9.1 tarball. The version of util-macros used to
    build the 1.9.1 tarball was modified and could cause problems
    due to the absence of the -fno-strict-aliasing CFLAG. This
    tarball was packaged using the unmodified util-macros.
    This additionally contains a fix for a regression in XQuartz
    found by Christof Wolf.
* Mon Oct 25 2010 sndirsch@novell.com
- commit-5c6a2f9.diff
  * retain obsolete pixmapPrivate, just for ABI compatibility
  * reenable patch
* Sun Oct 24 2010 sndirsch@novell.com
- xorg-server 1.9.1 (final release)
  * functionally equivalent to xorg-server 1.9.0.902
* Sat Oct 23 2010 sndirsch@novell.com
- disable commit-5c6a2f9.diff for now
* Fri Oct 22 2010 sndirsch@novell.com
- commit-5c6a2f9.diff
  xfree86: Kill pixmapPrivate with a vengeance (v2)
  ScrnInfo->pixmapPrivate only existed in order to catch invalid
  access to the framebuffer by making the backing data NULL across
  the VT switch. This was causing more confusion in the higher
  layers during mode setting without any real benefit, so remove
  it. v2: Kill ShadowModifyPixmapHeader() as well. (ABI change!)
* Fri Oct 15 2010 sndirsch@novell.com
- xorg-server 1.9.0.902
  * This release fixes an input regression introduced in 1.9.1 as
    well as some additional memory management issues.
- obsoletes vbe-bufferoverflow.diff
* Fri Oct 15 2010 coolo@novell.com
- Xvfb requires xkb rules, so adjust requires of the extra package
* Fri Oct  1 2010 sndirsch@novell.com
- xorg-server 1.9.0.901
  * This is the first release candidate for xorg-server-1.9.1.
    We've picked up fixes for some crashers and memory management
    problems as well as some minor new features including RandR
    support in XQuartz, 18bpp support in xfree86, and support for
    the nds32 architecture in xfree86.
- adjusted zap_warning_xserver.diff
* Wed Aug 25 2010 mhopf@novell.com
- Use-external-tool-for-creating-backtraces-on-crashes.patch,
  xorg-backtrace:
  Use external script /usr/bin/xorg-backtrace for creating reasonable
  backtraces upon crashes.
* Mon Aug 23 2010 sndirsch@suse.de
- set VIDEO_ABI_VERSION = 8 and INPUT_ABI_VERSION = 11 in specfile
* Mon Aug 23 2010 sndirsch@suse.de
- xorg-server 1.9.0
  * obsolete patches:
  - dmx-silly.patch
  - fixed-SYNC-extension-trigger-BlockHandler-test.diff
  - sw_cursor_on_randr.patch
  - xorg-evdev-conf.diff
  - xorg-server-commit-21ed660.diff
  - xorg-server-revert-event-mask.patch
  - xorg-x11-server-gl-apps-crash.patch
  * adjusted patches
  - 0001-Fix-segfault-when-killing-X-with-ctrl-alt-backspace.patch
  - 0001-Xinput-Catch-missing-configlayout-when-deleting-dev.patch
  - CVE-2010-2240-tree_depth_limit.patch
  - cache-xkbcomp-output-for-fast-start-up.patch
  - confine_to_shape.diff
  - driver-autoconfig.diff
  - fpic.diff
  - xorg-detect-psb.patch
  - xorg-server-1.8.0.diff
  - xorg-server-nohwaccess.diff
  - xorg-server-option_libxf86config.diff
  - xorg-server-xf4vnc.patch
  - xserver-1.6.1-nouveau.patch
  - xserver-bg-none-root.patch
  * vbe-bufferoverflow.diff
  - fixes vbe buffer overflow
- disabled vnc build for now (standalone server + module)
* Thu Aug 19 2010 max@suse.de
- Replaced the previous xdmcp fix with a simpler approach that
  doesn't cause login problems in xdm and kdm. (bnc#625593)
* Tue Aug 17 2010 sndirsch@suse.de
- CVE-2010-2240-address_space_limit.patch/
  CVE-2010-2240-tree_depth_limit.patch
  * xorg stack/heap overlap fix (bnc #618152)
* Mon Aug 16 2010 sndirsch@suse.de
- xorg-server-commit-21ed660.diff
  * dix: make DeviceEvent coordinates signed for Xinerama
    (bnc #628295, bfo #24986)
* Tue Aug 10 2010 sndirsch@suse.de
- xorg-server-revert-event-mask.patch
  * locked up mouse event mask patch (bnc #619034)
* Mon Aug  9 2010 vuntz@opensuse.org
- Add xorg-x11-server-gl-apps-crash.patch to fix crash with GL
  applications. See bnc#617651. The patch is taken from upstream on
  the server-1.8-branch and simply updates the glx/ and
  hw/xfree86/dri2/ directories.
* Wed Aug  4 2010 sndirsch@suse.de
- use configure option "--with-sha1=libcrypto" to fix also plain
  rpmbuilds (bnc #627872)
* Thu Jul  8 2010 max@suse.de
- Fix some shortcomings in the xdmcp implementation. It used to
  suppress loopback addresses from the list of potential display
  addresses to report to xdm, even when talking to xdm through
  a loopback address. Now only display addresses of the same kind
  as the xdm connection are reported to xdm.
  This most notably helps Xvnc servers contacting the local xdm,
  because they were severely affected by the suppression of
  loopback addresses.
* Mon Jun 28 2010 sndirsch@suse.de
- missing_font_paths.diff:
  * added /usr/share/fonts/{misc/sgi,truetype} to core font
    rendering default path; always use ":unscaled" for bitmap
    font paths (bnc #616400)
* Fri May 28 2010 sndirsch@suse.de
- xorg-detect-psb.patch
  * remove again "intellegacy" from driver autoconfiguration; that
    reverts previous change (bnc #608315)
* Sun May  9 2010 sndirsch@suse.de
- xorg-detect-psb.patch
  * added "intellegacy" as fallback for "intel" (gets active if
  'nomodeset' is set as kernel option) since there is now a new
  package for the older intel driver, which still has UMS support
* Wed Apr 28 2010 sndirsch@suse.de
- remove Xdmx manual page from xorg-x11-server, since it's already
  in xorg-x11-server-extra
* Mon Apr 26 2010 eich@suse.de
- Updated "Prevent XSync Alarms from senslessly calling CheckTrigger()"
  to make sure SyncTriggerInit() readds trigger to counter (bnc #584919).
* Mon Apr 26 2010 sndirsch@suse.de
- Xdmx was disabled in favor of Nomad repository but it is
  apparently dead (no Xdmx for OpenSUSE 11.2, last build from
  early 2009). This patch re-enables Xdmx with some silly typo
  fixed (dmx-silly.patch). Contributed by <zawel1@gmail.com>.
* Wed Apr 21 2010 eich@suse.de
- Prevent XSync Alarms from senslessly calling CheckTrigger() when inactive.
  If an XSync Alarm is set to inactive there is no need to check if a trigger
  needs to fire. Doing so if the counter is the IdleCounter will put the
  server on 100 percent CPU load since the select timeout is set to 0
  (bnc #584919).
* Sat Apr 10 2010 sndirsch@suse.de
- specfile cleanup
- removed no longer useful xlog2xconf.sh
* Sat Apr 10 2010 sndirsch@suse.de
- adjusted moblin-xserver-no-root-2.patch, renamed it to
  xorg-server-nohwaccess.diff and enable it by default
- rename moblin-xorg-x11-nonroot-vesa.patch to
  xorg-x11-nonroot-vesa.patch
- removed obsolete patch 'xserver-boottime.patch'
* Thu Apr  8 2010 eich@novell.com
- Adapted and fixed 'noroot-background' patch originally coming from
  the Moblin project and enable by default.
* Thu Apr  8 2010 eich@suse.de
- On ia64 the Xserver brings its own PIO functions (inb, outb, ...).
  These are supposed to overrule the ones provided by glibc.
  Unfortunately this doesn't seem to work under all circumstances.
  Therefore use inX/outX_ia64 and set appropriate defines.
* Thu Apr  8 2010 eich@suse.de
- Fix SIG11 on VT switch when using SW cursor with RandR (bnc #592614).
* Thu Apr  8 2010 ro@suse.de
- fix evdev config file (use the one from xserver upstream)
* Tue Apr  6 2010 ro@suse.de
- fix libxf86config (resolve references)
* Tue Apr  6 2010 sndirsch@suse.de
- fix_fglrx_screendepth_issue.patch
  * hardcode default color depth of fglrx driver to 24bit to fix
    video driver autoconfiguration (bnc #593878)
* Fri Apr  2 2010 sndirsch@suse.de
- update to 1.8
- obsoletes xorg-server-walk_drivers.diff
- adjusted xorg-server-xf4vnc.patch
- xorg-server-1.8.0.diff
  * install evdev config file to the right directory
* Fri Mar 26 2010 sndirsch@suse.de
- xorg-server-walk_drivers.diff:
  * updated patch working more cleanly, fixed coding style, added
    comments (Rüdiger Oertel)
* Wed Mar 24 2010 sndirsch@suse.de
- disabled udev support for openSUSE <= 11.2 (bnc #589997)
* Wed Mar 24 2010 ro@suse.de
- re-do xorg-server-walk_drivers.diff again, different approach
  create screen sections for each possible drivers
  now it is really using the first driver as in full autoconfig
* Tue Mar 23 2010 sndirsch@suse.de
- update to 1.7.99.902
- fixed font path ("--with-fontrootdir")
* Mon Mar 22 2010 ro@suse.de
- xserver-1.6.1-nouveau.patch (from fedora)
  Also, don't treat DRI setup failure as an error for nouveau.
* Mon Mar 22 2010 ro@suse.de
- rework xorg-server-walk_drivers.diff
* Sun Mar 21 2010 ro@suse.de
- re-implement walking list of possible drivers to find a working
  one
* Thu Mar 18 2010 ro@suse.de
- update to 1.7.99 to get rid of hal
  - refresh patches
  - drop p_ia64-console.diff
- remove hal-devel from buildrequires
- add libudev-devel to buildrequires
- add --enable-config-udev to configure
* Wed Mar 17 2010 ro@suse.de
- drop un-applied patches
  p_pci-off-by-one.diff.ia64
  xorg-x11-server-1.2.99-unbreak-domain.patch
  ia64linuxPciInit.diff
  exa-greedy.diff
  commit-c941479.diff
  moblin-hw-xf86-modes-Set-crtc-mode-rotation-transform-befo.patch
  moblin-xfree86-move-didLock-assignment-down-to-where-the-f.patch
  moblin-randr-fix-operation-order-so-that-rotation-transfor.patch
* Wed Mar 17 2010 sndirsch@suse.de
- update to 1.7.6
  * reintrocued record extension
  * bugfixes
* Sat Feb 20 2010 sndirsch@suse.de
- update to 1.7.5
  * Only four fixes since the RC, with the fix for 25640 being
    rather noteworthy - if your X server crashed on replugging
    keyboards (or using a KVM), you're encouraged to upgrade.
  - dix: restore lastDeviceEventTime update in dixSaveScreens
  - Don't double-swap the RandR PropertyNotify event
  - Xi: reset the sli pointers after copying device classes.
    (bfo #25640)
  - RENDER: Fix gradient and solid fill pictures with Xinerama,
    and misc cleanup
- obsoletes
  0001-Don-t-double-swap-the-RandR-PropertyNotify-event.patch
* Fri Feb 12 2010 lchiquitto@novell.com
- 0001-Don-t-double-swap-the-RandR-PropertyNotify-event.patch
  * The event is swapped in randr.c/SRROutputPropertyNotifyEvent,
    so it should not be swapped again here.
    (bnc #573446, bfo #26511)
* Sat Jan 16 2010 sndirsch@suse.de
- set VIDEO_ABI_VERSION = 6 and INPUT_ABI_VERSION = 7 in specfile
* Thu Jan 14 2010 ro@suse.de
- update to 1.7.4
  - obsoletes acpi_events.diff
  - obsoletes loadmod-bug197195.diff
  - obsoletes events.diff
  - obsoletes acpi-warning.diff
  - obsoletes fbdev_fallback_fail_fix.diff
  - obsoletes bug-507190_xorg-x11-server-bnc381139-randr-reprobe-on-unsuspend.diff
  - obsoletes keyrelease-1.5.2.diff
  - obsoletes 0001-Unclaim-PCI-slot-if-driver-probing-fails.patch
  - obsoletes 0001-Fix-sporadic-segfault-on-resume-with-intel-KMS-due-t.patch
  - obsoletes bug532341.diff
  - obsoletes no-return-in-nonvoid-function.diff
  - adjusted 0001-Fix-segfault-when-killing-X-with-ctrl-alt-backspace.patch
  - adjusted bitmap_always_unscaled.diff
  - adjusted bug-197858_dpms.diff
  - adjusted cache-xkbcomp-output-for-fast-start-up.patch
  - adjusted driver-autoconfig.diff
  - adjusted fixed-SYNC-extension-trigger-BlockHandler-test.diff
  - adjusted fpic.diff
  - adjusted missing_font_paths.diff
  - adjusted p_default-module-path.diff
  - adjusted p_ia64-console.diff
  - adjusted p_xorg_acpi.diff
  - adjusted xorg-detect-psb.patch
  - adjusted xorg-server-xf4vnc-disable-dmxvnc.diff
  - adjusted xorg-server-xf4vnc-fix.diff
  - adjusted xorg-server-xf4vnc.patch
  - adjusted xorg-x11-server.changes
  - adjusted xorg-x11-server.spec
  - adjusted zap_warning_xserver.diff
- removed truetype_fontpath.diff
- removed libdri_noPanoramiXExtension_symbol.patch
- exa-greedy.diff not applied
- fixed xorg-detect-psb.patch:
  rewrite to use second level switch statement for device_id
- /usr/$lib/X11/Options is gone
  (Remove xorgcfg 'Options' list.)
* Sun Dec 13 2009 sndirsch@suse.de
- added xlog2xconf, which is a script to create a minimal xorg.conf
  extracted from Xorg.<DISPLAY>.log
* Sun Nov 29 2009 sndirsch@suse.de
- driver-autoconfig.diff:
  * VIA chipsets: switched to "via" as first try since "via" is no
    longer renamed to "chrome9" in -chrome9 driver package and
  - unichrome driver package now disables the "via" wrapper
* Fri Nov 27 2009 sndirsch@suse.de
- missing_font_paths.diff
  * added /usr/share/fonts/{URW,cyrillic} to font paths
    (bnc #558915)
* Mon Nov  2 2009 sndirsch@suse.de
- build Xserver again with '-O2' instead of '-O0', which had been
  an unintentional change (bnc #551789)
* Mon Oct 19 2009 sndirsch@suse.de
- add 'Option "AutoAddDevices" "off"' to xorg.conf only as
  documented comment, since it caused a lot of confusion
  (bnc #548085 and various others)
* Mon Oct 12 2009 sndirsch@suse.de
- xorg-server 1.6.5
  * This release fixes the fact that 1.6.4 would crash on drivers
    that still tried to initialize the DGA extension. It also has
    a minor improvement for Xephyr to support nesting within an
    existing window at a different depth.
- obsoletes dga-removal-fix.diff
* Fri Oct  9 2009 sndirsch@suse.de
- since we no longer use xorg.conf make ZapWarning the default
  (bnc #545590)
* Thu Oct  8 2009 eich@suse.de
-  Fix segfault when killing X with ctrl-alt-backspace. (bnc #545363)
  * The damage structure for the cursor is not deregistered before
    deallocation, causing a subsequent DamageUnregister () to segfault.
    The problem may leave the text console unrestored.
    (0001-Fix-segfault-when-killing-X-with-ctrl-alt-backspace.patch)
* Wed Oct  7 2009 eich@suse.de
- 0001-Check-harder-for-primary-PCI-device.patch (bnc #545458)
  * Primary PCI devices are identified by checking for an 'PCIINFOCLASSES'
    device which is VGA and has access to the memory bars enabled.
    If there should be more than one device for which this is true
    redo the check and also check if IO resoures are also enabled,
    if this still doesn't turn up a unique result also check for
    the presence of a BIOS rom.
* Wed Oct  7 2009 sndirsch@suse.de
- driver-autoconfig.diff
  * GeForce 6150SE support broken on nv (bnc #465190/544674)
* Thu Oct  1 2009 sndirsch@suse.de
- dga-removal-fix.diff
  * Here's an updated patch -- removes the _X_INTERNAL from the .c
    files, renames xf86DiDGAInit to _xf86_di_dga_init_internal,
    and renames xf86DiDGAReInit to _xf86_di_dga_reinit_internal.
* Tue Sep 29 2009 sndirsch@suse.de
- dga-removal-fix.diff
  * "Removing DGA ended up breaking any drivers calling into the old
    xf86DiDGAInit function as it tried to see if DGA was already
    enabled and ended up crashing if the VT wasn't completely
    initialized. Oops."
* Mon Sep 28 2009 sndirsch@suse.de
- xorg-server 1.6.4
  * fbdevhw: Test for graphics:fb%%d as well as graphics/fb%%d
  * render: return the supported version rather than just passing
    the proto's version
  * xfree86/modes: Remove all framebuffer support from DGA
  * dri2: Don't crash if pPriv is NULL.
  * Don't send events through the master if the device has
    SendCoreEvents off.
  * Don't reset the lastDeviceEventTime when doing DPMS actions
  * dix: append "built-ins" to the font path in SetDefaultFontPath
* Mon Sep 28 2009 sndirsch@suse.de
- bug532341.diff
  * fixes Xserver crash when running x11perf -shmputxy10 test case
    (bnc #532341, bfo #23298)
* Mon Sep 21 2009 mhopf@novell.com
- Less intrusive fix for server segfault. Should fix fdo #24010 (memleak).
* Thu Sep 10 2009 sndirsch@suse.de
- %%post: modify xorg.conf if required
  * do not change input driver behaviour for existing X.Org
    configurations
* Wed Sep  9 2009 sndirsch@suse.de
- moblin-use_preferred_mode_for_all_outputs.diff
  * use each outputs preferred mode (bnc #537488)
* Tue Sep  8 2009 mhopf@novell.com
- Prefer locally defined symbols in modules (bnc #534768).
* Fri Sep  4 2009 mhopf@novell.com
- 0001-Fix-sporadic-segfault-on-resume-with-intel-KMS-due-t.patch:
  Fixes segfaults with intel and KMS upon resume (only occuring sporadically).
* Thu Aug 27 2009 eich@suse.de
- Update to 1.6.4 RC1, adapted patches.
* Fri Aug 14 2009 sndirsch@suse.de
- 0001-config-don-t-shutdown-the-libhal-ctx-if-it-failed-to.patch
  * no longer need to revert commit c941479 (bnc #528397, bfo #23213)
* Tue Aug 11 2009 sndirsch@suse.de
- revert commit c941479 (bnc #528397)
* Tue Aug  4 2009 eich@suse.de
- Resynced with patches from Intel's Moblin project.
- Updated patches to aply cleanly again.
* Sat Aug  1 2009 sndirsch@suse.de
- xorg-server 1.6.3
  * This mostly just collects a bunch of minor fixes since 1.6.2.
    Two notable inclusions are:
  - Replacing dixLookupResource with dixLookupResourceByType,
    dixLookupResourceByClass. This returns us to having two
    resource lookup functions, but this time we have a more
    sensible name and argument set.
  - Fixing RandR transforms for drivers providing set_mode_major.
    These patches were originally slated to land in 1.6.2 but
    I missed them somehow.
- obsoletes commit-cadf65a.diff
* Wed Jul  8 2009 sndirsch@novell.com
- xorg-server 1.6.2
  * This is the second update to the 1.6 version and is designed
    to be a drop-in compatible version with various bug fixes and
    other improvements.
- obsoletes various patches
  * bug-507190_xorg-x11-server-bnc381139-randr-fix-timestamps.diff
  * includes-fix.diff
  * security-Fix-a-crash-caused-by-wrong-ordering-of-fo.patch
  * security-Grant-untrusted-windows-remove-access-on-a.patch
  * security-Revert-behavior-of-extension-access-for-co.patch
- adjusted zap_warning_xserver.diff
* Thu Jul  2 2009 mhopf@novell.com
- Adapt vnc patches to changes in input infrastructure
  (fixes bnc #508553)
* Wed Jun 24 2009 mhopf@novell.com
- Unclaim PCI slot if driver probing fails (fixes bnc #511529)
* Fri Jun 19 2009 sndirsch@suse.de
- includes-fix.diff
  * build fix
- truetype_fontpath.diff
  * added /usr/share/fonts/truetype to default font path
* Thu Jun 11 2009 sndirsch@suse.de
- use %%moblin define in specfile
* Wed Jun 10 2009 sndirsch@suse.de
- xserver-1.5.0-bg-none-root.patch
  * removed patch for compalloc.c, which hurts on Moblin
- disabled xserver-1.5.0-bg-none-root.patch (only useful for Moblin)
* Tue Jun  9 2009 sndirsch@suse.de
- diabled build of Xdmx since it conflict's with NOMAD's Xdmx
  (bnc #511269)
* Fri Jun  5 2009 sndirsch@suse.de
- driver-autoconfig.diff
  * ati ==> fglrx --> radeonhd --> ati
  * nv ==> nvidia --> nouveau --> nv (FATE #305109)
  * openchrome ==> chrome9 --> openchrome --> unichrome
  * registered vboxvideo
- obsoletes radeonhd.diff/radeonhd.h
* Fri Jun  5 2009 sndirsch@suse.de
- keyrelease-git.diff
  * xkb: Don't press+release keys on key events. Fixes submission
    of F7 to apps on switch from console for drivers that switch
    fast enough (bnc #141443).
* Thu Jun  4 2009 sndirsch@suse.de
- autoconfig_fallback_fbdev_first.diff
  * fallback to fbdev first, then vesa instead of the other way
    round
* Tue Jun  2 2009 eich@suse.de
  Frederico's patches to support reprobing of connected displays on EnterVT
  and fixes to set event timestamps properly.
- Re-probe RANDR outputs on laptop unsuspend.
- Make RANDR 'set' timestamps follow client specified time.
- Add missing fields to SRR*NotifyEvent().
* Tue Jun  2 2009 eich@suse.de
- Patches taken from Moblin:
  * security: Grant untrusted windows remove access on all windows.
  * security: Fix a crash caused by wrong ordering of format arguments.
  * security: Revert behavior of extension access for compatibility.
  * Autodetect Plousbo chips.
  * add -nb command line option to supress root window background stet
    on startup.
  * cache xkb output for fast startup.
  * make noPanoramiXExtension symbol local and initialize.
* Thu May 28 2009 sndirsch@suse.de
- fbdev_fallback_fail_fix.diff
  * fix fbdev fallback failure if no xorg.conf exists; fbdev driver
    complained about required BusID (Egbert Eich)
* Thu Apr 30 2009 sndirsch@suse.de
- instead of require do provide
  INPUT_ABI_VERSION/VIDEO_ABI_VERSION to fix dependancy loop
* Thu Apr 30 2009 sndirsch@suse.de
- xkeyboard-config should be required by xorg-x11-driver-input
- require INPUT_ABI_VERSION = 4 (provided by xorg-x11-driver-input)
- require VIDEO_ABI_VERSION = 5 (provided by xorg-x11-driver-video)
- require libpixman-1-0 >= 0.15.2
* Tue Apr 28 2009 sndirsch@suse.de
- enable DRI2 build
* Tue Apr 14 2009 sndirsch@suse.de
- xorg-server 1.6.1
* Mon Mar 23 2009 sndirsch@suse.de
- fixed-SYNC-extension-trigger-BlockHandler-test.diff (bnc #472046)
  * Reworked ComputeBracketValues():
  * Reworked previous patch to IdleTimeBlockHandler() (commit 1f4fb022)
  (Egbert Eich)
* Tue Mar 10 2009 sndirsch@suse.de
- commit-cadf65a.diff
  * randr: Nuke broken set_origin shortcut. Shortcut is impossible
    to implement this way, because we don't know for sure whether
    the crtc of an output has changed or not. (bnc #482838)
* Mon Mar  9 2009 mmarek@suse.cz
- renamed modprobe config to /etc/modprobe.d/50-nvidia.conf
  (required by new module-init-tools).
* Sun Mar  8 2009 sndirsch@suse.de
- radeonhd.diff/radeonhd.h:
  * prefer radeonhd for autoconfig for ATI >= R500
* Sun Mar  8 2009 sndirsch@suse.de
- added hal-devel to BuildRequires for input driver configuration
  support via HAL, e.g. evdev
* Wed Mar  4 2009 sndirsch@suse.de
- removed randr12-8d230319040f0a7f72231da2bf5ec97dc3612e21.diff;
  probably a wrong patch since this commit has been reverted right
  after by commit b4193a2eee80895c5641e77488df0e72a73a3d99 again
- no longer overwrite xorg.conf with an obsolete one; obsoletes
  disable-root-xorg_conf.diff
* Tue Mar  3 2009 sndirsch@suse.de
- regenerated xorg-server-xf4vnc.patch (still disabled)
* Fri Feb 27 2009 sndirsch@suse.de
- xorg-server 1.6.0
- temporarily disabled build of Xvnc/libvnc.so
- obsoletes 64bit-portability-issue.diff, 64bit.diff,
  commit-59f9fb4b8.diff, commit-a9e2030.diff, dga_cleanup.diff,
  miPointerUpdate-crashfix.diff, p_mouse_misc.diff,
  ps_showopts.diff, unplugged_monitor_crashfix.diff
- adjusted 0001-Xinput-Catch-missing-configlayout-when-deleting-dev.patch,
  bitmap_always_unscaled.diff, confine_to_shape.diff, fbdevhw.diff,
  p_ia64-console.diff, randr1_1-sig11.diff, xephyr.diff,
  xorg-server-xf4vnc.patch, zap_warning_xserver.diff
* Tue Feb 24 2009 sndirsch@suse.de
- bug474071-fix1.diff
  * fixes Xserver issue of bnc #474071
* Mon Feb 16 2009 sndirsch@suse.de
- /var/X11R6/bin no longer covered by FHS; switched to
  /var/lib/X11 (bnc #470969)
* Sat Jan 31 2009 schwab@suse.de
- Provide proper fallback when legacy_mem is not available.
* Thu Jan 29 2009 sndirsch@suse.de
- reenabled Security extension (bnc #470601)
* Fri Jan 16 2009 sndirsch@suse.de
- sysconfig.displaymanager.template
  * reintroducing DISPLAYMANAGER_XSERVER sysconfig variable, since
    it's still used by proprietary driver packages (bnc #466583)
* Sat Dec 20 2008 sndirsch@suse.de
- xorg-server-xf4vnc-clientTimeout.diff
  * fixes vnc client timeout handling (bnc #441935)
* Fri Nov 28 2008 sndirsch@suse.de
- dpms_screensaver.diff
  * DMPS calls dixSaveScreens() when turned on but not when turned
    off. In most cases this is irrelevant as DPMS is done when a
    key is hit in which case dixSaveScreens() will be called to
    unblank anyhow. This isn't the case if we use xset (or the
    DPMS extension directly) to unblank. (bnc #439495)
* Wed Nov 26 2008 sndirsch@suse.de
- rename "i810" driver entry in xorg.conf to "intel" during update
  (bnc #448458)
* Fri Nov 21 2008 sndirsch@suse.de
- commit-a9e2030.diff
  * int10: Do an mprotect(..,PROT_EXEC) on shmat()ed memory
    ranges. When the linux kernel sets the NX bit vm86 segfaults
    when it tries to execute code in memory that is not marked
    EXEC. Such code gets called whenever we return from a VBIOS
    call to signal the calling program that the call is actually
    finished and that we are not trapping for other reasons
    (like IO accesses). Use mprotect(2) to set these memory
    ranges PROT_EXEC. (bnc #443440)
* Thu Nov 13 2008 sndirsch@suse.de
- 0001-Xinput-Catch-missing-configlayout-when-deleting-dev.patch
  * In DeleteInputDeviceRequest (xf86Xinput.c), we access idev
    members even if idev is null. This takes down the xserver
    hard in some cases (kernel SIGABRT), and segfaults on other
    cases (Luc Verhaegen).
* Sat Nov  8 2008 sndirsch@suse.de
- commit-59f9fb4b8.diff
  * XAA PixmapOps: Sync before accessing unwrapped callbacks.
    (bnc #435791)
- obsoletes XAA_pixmap_sync.diff
* Fri Nov  7 2008 sndirsch@suse.de
- XAA_pixmap_sync.diff
  * By adding a line with SYNC_CHECK to the XAA_PIXMAP_OP_PROLOGUE
    macro, all XAA pixmap callbacks now properly wait for the
    hardware to be synced before calling the (next) unwrapped
    callback. This effectively clears up all the drawing issues
    we are seeing. (bnc #435791)
* Thu Nov  6 2008 sndirsch@suse.de
- vidmode-sig11.diff
  * fixes Sig11 in vidmode extension (bnc #439354)
* Wed Nov  5 2008 sndirsch@suse.de
- unplugged_monitor_crashfix.diff
  * prevent monitor from crashing during startup if statically
    configured external has been unplugged (bfo #18246)
* Tue Nov  4 2008 sndirsch@suse.de
- removed glitz-devel from BuildRequires (bnc #441549)
* Mon Oct 27 2008 sndirsch@suse.de
- build and install libxf86config + header files also on s390(x)
  (bnc #432738)
* Mon Oct 27 2008 sndirsch@suse.de
- removed p_ppc_domain_workaround.diff/ppc.diff to fix Xserver
  start on ppc (bnc #437695)
* Sat Oct 25 2008 sndirsch@suse.de
- xorg-server-xf4vnc-busyloop.diff
  * prevent Xvnc from busylooping when client disconnects
  (bnc #403901)
* Fri Oct 17 2008 sndirsch@suse.de
- miPointerUpdate-crashfix.diff
  * fixes Xserver crash at startup with ELO touchscreen
    (bnc #436435)
* Sat Oct 11 2008 sndirsch@suse.de
- xorg-server 1.5.2
  * int10: Remove useless check.
  * int10: Don't warn when scanning for devices we don't have.
  * int10: Fix a nasty memory leak.
  * Revert "Array-index based devPrivates implementation."
  * EDID: Catch monitors that encode aspect ratio for physical
    size.
  * Remove usage of mfbChangeWindowAttributes missed in
    e4d11e58c...
  * only build dri2 when DRI2 is enabled
  * Array-index based devPrivates implementation.
  * Fix GKVE with key_code > 255
  * xkb: fix use of uninitialized variable.
  * DGA: Fix ProcXF86DGASetViewPort for missing support in driver.
  * xkb: fix core keyboard map generation. (bfo #14373)
  * xkb: squash canonical types into explicit ones on core
    reconstruction.
  * Check nextEnabledOutput()'s return in bestModeForAspect()
- obsoletes xorg-server-commit-d1bb5e3.diff
* Fri Oct 10 2008 sndirsch@suse.de
- dga_cleanup.diff
  * DGA: Mash together xf86dga.c and xf86dga2.c for a client state
    tracking fix.
  * DGA: Track client state even when using old style DGA. This
    fixes the issue that a badly killed DGA will keep on hogging
    mode/framebuffer/mouse/keyboard. (bnc #310232)
* Thu Oct  9 2008 sndirsch@suse.de
- xorg-server-commit-d1bb5e3.diff
  * DGA: Fix ProcXF86DGASetViewPort for missing support in driver.
    Fixes a segfault when trying to activate a DGA mode without
    checking whether DGA modesetting is at all possible.
    (Luc Verhaegen)
* Mon Sep 29 2008 sndirsch@suse.de
- make use of %%configure macro
* Tue Sep 23 2008 sndirsch@suse.de
- xorg-server 1.5.1 (planned for final X.Org 7.4 release)
  * Conditionalize Composite-based backing store on
    pScreen->backingStoreSupport. (Aaron Plattner)
  * Move RELEASE_DATE below AC_INIT. (Adam Jackson)
  * exa: disable shared pixmaps (Julien Cristau)
  * Fix panoramiX request and reply swapping (Peter Harris)
* Mon Sep 22 2008 sndirsch@suse.de
- disabled build of optional "xcliplist" module (bnc #428189)
* Sat Sep 13 2008 sndirsch@suse.de
- added /usr/lib64/X11 dir to filelist to fix build on 64bit
  platforms
* Thu Sep 11 2008 sndirsch@suse.de
- bumped release number to 7.4
* Wed Sep  3 2008 sndirsch@suse.de
- xorg-server 1.5.0
  * almost certainly the server that will go into Xorg 7.4,
    which is supposed to be available in a day or two
- obsoletes commit-5930aeb.diff/commit-78f50cd.diff
* Thu Aug 28 2008 sndirsch@suse.de
- commit-5930aeb.diff/commit-78f50cd.diff
  * obsoletes reverting of Mesa commit 1724334 (bfo #17069)
* Fri Aug  8 2008 sndirsch@suse.de
- commit-50e80c3.diff obsolete now (bnc #415680)
- commit-f6401f9.diff obsolete
* Wed Aug  6 2008 schwab@suse.de
- Fix crash in Xvnc when handling selections.
* Tue Aug  5 2008 sndirsch@suse.de
- enabled build of record extension, which has been disabled
  upstream for whatever reason
* Fri Aug  1 2008 sndirsch@suse.de
- xorg-server-xf4vnc-abi-version.diff
  * raised ABI version for xorg-server 1.5(-pre)
* Thu Jul 24 2008 sndirsch@suse.de
- xorg-server 1.4.99.906
- obsoletes commit-a18551c.diff
* Tue Jul 22 2008 sndirsch@suse.de
- exa-greedy.diff
  * Make sure exaMigrateTowardFb/Sys end up calling exaCopyDirty
    (bfo #16773)
* Fri Jul 18 2008 schwab@suse.de
- Kill useless warning.
* Mon Jul 14 2008 sndirsch@suse.de
- improved ppc/ppc64 patch once more
* Fri Jul 11 2008 sndirsch@suse.de
- improved ppc/ppc64 patch
- Xvfb (xorg-x11-server-extra) requires Mesa (swrast_dri.so) now
* Thu Jul 10 2008 sndirsch@suse.de
- xorg-server-xf4vnc-TranslateNone.diff
  * supposed to fix Xvnc crash when VNC client is running on a
    display with the same color depth (bnc #389386)
- ppc.diff
  * fixes build on ppc/ppc64
* Thu Jul 10 2008 sndirsch@suse.de
- enabled build of Xvnc/libvnc
- xorg-server-xf4vnc-disable-dmxvnc.diff
  * disabled VNC feature in DMX to fix VNC build
* Thu Jul 10 2008 sndirsch@suse.de
- updated to new vnc patch "xorg-server-xf4vnc.patch "by Dan
  Nicholson, which is still disabled due to build errors
- obsoletes the following patches:
  * xorg-server-1.4-vnc-64bit.diff
  * xorg-server-1.4-vnc-disable_render.diff
  * xorg-server-1.4-vnc-fix.patch
  * xorg-server-1.4-vnc-memory.diff
  * xorg-server-1.4-vnc-render_sig11.diff
  * xorg-server-1.4-vnc.patch
* Tue Jul  8 2008 sndirsch@suse.de
- commit-a18551c.diff
  * Fix GLX in Xvfb and kdrive.
    Xvfb could no longer be started: "Xvfb: symbol lookup error:
    /usr/lib/dri/swrast_dri.so: undefined symbol:
    _glapi_add_dispatch". This is fixed now.
- removed no longer appliable patch 'p_xf86Mode.diff'
* Fri Jul  4 2008 sndirsch@suse.de
- xorg-server-1.4.99.905
  * obsolete patches
  - XAANoOffscreenPixmaps.diff
  - bug227111-ddc_screensize.diff
  - commit-184e571.diff
  - commit-29e0e18.diff
  - commit-c6c284e.diff
  - commit-f7dd0c7.diff
  - commit-fa19e84.diff
  - commit-feac075.diff
  - glx-align.patch
  - mfb_without_xorg.diff
  - p_ValidatePci.diff
  - p_vga-crashfix.diff
  - xkb_action.diff
  - xorg-server.diff
  - xprint.diff
  - xserver-mode-fuzzy-check.diff
  * new patches
  - 64bit-portability-issue.diff
  - no-return-in-nonvoid-function.diff
  * adjusted patches
  - bitmap_always_unscaled.diff
  - disable-root-xorg_conf.diff
  - p_ppc_domain_workaround.diff
  - pixman.diff
  - ps_showopts.diff
  - xorg-server-1.4-vnc.patch
  - bug-197858_dpms.diff
- Mesa sources no longer required for xorg-server 1.5
- VNC patches + build disabled for now
- disabled some IA64 patches for now
* Fri Jun 13 2008 sndirsch@suse.de
- xorg-x11-Xvnc: added meta file for SuSEfirewall2 (bnc #398855)
* Wed Jun 11 2008 sndirsch@suse.de
- xorg-server 1.4.2
  * CVE-2008-2360 - RENDER Extension heap buffer overflow
  * CVE-2008-2361 - RENDER Extension crash
  * CVE-2008-2362 - RENDER Extension memory corruption
  * CVE-2008-1377 - RECORD and Security extensions memory corruption
  * CVE-2008-1379 - MIT-SHM arbitrary memory read
- obsoletes bfo-bug15222.diff
* Tue Jun 10 2008 sndirsch@suse.de
- xorg-server 1.4.1
  * Contains a few security and input fixes, some memory leak
    fixes, and a few misc bits.
  * obsolete patches:
  - CVE-2007-5760-xf86misc.diff
  - CVE-2007-6427-xinput.diff
  - CVE-2007-6428-TOG-cup.diff
  - CVE-2007-6429-shm_evi.diff
  - CVE-2008-0006-pcf_font.diff
  - commit-37b1258.diff
  - commit-a6a7fad.diff
  - remove_bogus_modeline.diff
  - xserver-1.3.0-xkb-and-loathing.patch
  * adjusted patches
  - xorg-server-1.4-vnc.patch
* Thu Jun  5 2008 sndirsch@suse.de
- bfo-bug15222.diff (bfo #15222, bnc #374318)
  * CVE-2008-2360 - RENDER Extension heap buffer overflow
  * CVE-2008-2361 - RENDER Extension crash
  * CVE-2008-2362 - RENDER Extension memory corruption
  * CVE-2008-1379 - MIT-SHM arbitrary memory read
  * CVE-2008-1377 - RECORD and Security extensions memory corruption
* Tue May 27 2008 sndirsch@suse.de
- xserver-mode-fuzzy-check.diff
  * Make mode checking more tolerant like in pre-RandR times.
* Mon May 26 2008 sndirsch@suse.de
- fix-dpi-values.diff
  * fixes DPI values for RANDR 1.2 capable drivers (bnc #393001)
* Fri May 16 2008 sndirsch@suse.de
- mention ZapWarning also in Xorg manual page (bnc #391352)
* Fri May 16 2008 sndirsch@suse.de
- xorg-server-1.4-vnc-render_sig11.diff
  * fixed sig11 in RENDER code (bnc #385677)
* Wed May 14 2008 sndirsch@suse.de
- disabled patch to disable RENDER support in Xvnc, since it broke
  24bit color depth support (bnc #390011)
* Mon May  5 2008 sndirsch@suse.de
- xorg-server-1.4-vnc-disable_render.diff
  * disabled RENDER support in Xvnc (bnc #385677)
* Mon Apr 21 2008 sndirsch@suse.de
- events.diff
  * eating up key events before going into the idle loop upon vt
    switch instead of after return (bnc #152522)
* Mon Apr 21 2008 sndirsch@suse.de
- xkb_action.diff
  * fixed remaining unitialized warning in X.Org (bnc #83910)
* Sun Apr 20 2008 sndirsch@suse.de
- fbdevhw.diff
  * screen blanking not supported by vesafb of Linux kernel
    (bnc #146462)
* Tue Apr 15 2008 sndirsch@suse.de
- no longer disable AIGLX by default
* Thu Apr 10 2008 sndirsch@suse.de
- XAANoOffscreenPixmaps.diff
  * disable Offscreen Pixmaps by default (bnc #376068)
* Wed Apr  9 2008 schwab@suse.de
- Fix another o-b-1 in pci domain support.
* Wed Apr  9 2008 sndirsch@suse.de
- randr1_1-sig11.diff
  * fixes Xserver crash when running xrandr on a different virtual
    terminal (Egbert Eich, bnc #223459)
* Mon Apr  7 2008 sndirsch@suse.de
- commit-37b1258.diff
  * possibly fixes unwanted autorepeat (bnc #377612, bfo #14811)
* Sat Apr  5 2008 sndirsch@suse.de
- bitmap_always_unscaled.diff
  * Default bitmap fonts should typically be set as unscaled (libv)
* Sat Apr  5 2008 sndirsch@suse.de
- update to Mesa bugfix release 7.0.3 (final) sources
* Wed Apr  2 2008 sndirsch@suse.de
- update to Mesa bugfix release 7.0.3 RC3 sources
* Mon Mar 31 2008 sndirsch@suse.de
- confine_to_shape.diff
  * fixes XGrabPointer's confine_to with shaped windows (bnc #62146)
* Thu Mar 20 2008 sndirsch@suse.de
- zap_warning_xserver.diff
  * implements FATE #302988: ZapWarning (Luc Verhaegen)
    Uses PCSpeaker for beep. Press once, beep. Press again within
    2s (which is ample), terminate. Documented in xorg.conf manpage.
- make the memory corruption fix by schwab a seperate patch to make
  sure it won't get lost the next time I update the VNC patch
* Wed Mar 19 2008 schwab@suse.de
- Fix vnc server memory corruption.
* Fri Mar  7 2008 sndirsch@suse.de
- commit-a6a7fad.diff
  * Don't break grab and focus state for a window when redirecting
    it. (bnc #336219, bfo #488264)
* Fri Feb 22 2008 sndirsch@suse.de
- update to Mesa bugfix release 7.0.3 RC2 sources
  * Fixed GLX indirect vertex array rendering bug (14197)
  * Fixed crash when deleting framebuffer objects (bugs 13507,
    14293)
  * User-defined clip planes enabled for R300 (bug 9871)
  * Fixed glBindTexture() crash upon bad target (bug 14514)
  * Fixed potential crash in glDrawPixels(GL_DEPTH_COMPONENT) (bug
    13915)
  * Bad strings given to glProgramStringARB() didn't generate
    GL_INVALID_OPERATION
  * Fixed minor point rasterization regression (bug 11016)
* Mon Feb  4 2008 sndirsch@suse.de
- added Requires:xkeyboard-config to xorg-x11-server
* Fri Feb  1 2008 sndirsch@suse.de
- commit-50e80c3.diff:
  * never overwrite realInputProc with enqueueInputProc
    (bnc#357989, bfo#13511)
* Thu Jan 24 2008 sndirsch@suse.de
- only switch to radeon driver in %%post if radeonold driver is no
  longer available (Bug #355009)
- some more cleanup in %%post
* Thu Jan 24 2008 schwab@suse.de
- Move manpage to the sub package that provides the binary.
* Wed Jan 23 2008 sndirsch@suse.de
- update to Mesa bugfix release 7.0.3 RC1 sources
  * Added missing glw.pc.in file to release tarball
  * Fix GLUT/Fortran issues
  * GLSL gl_FrontLightModelProduct.sceneColor variable wasn't
    defined
  * Fix crash upon GLSL variable array indexes (not yet supported)
  * Two-sided stencil test didn't work in software rendering
  * Fix two-sided lighting bugs/crashes (bug 13368)
  * GLSL gl_FrontFacing didn't work properly
  * glGetActiveUniform returned incorrect sizes (bug 13751)
  * Fix several bugs relating to uniforms and attributes in GLSL
    API (Bruce Merry, bug 13753)
  * glTexImage3D(GL_PROXY_TEXTURE_3D) mis-set teximage depth field
* Mon Jan 21 2008 sndirsch@suse.de
-  updated patch for CVE-2007-6429 once more (X.Org Bug #13520)
  * Always test for size+offset wrapping.
* Sun Jan 20 2008 sndirsch@suse.de
- updated patch for CVE-2007-6429 (Bug #345131)
  * Don't spuriously reject <8bpp shm pixmaps.
    Move size validation after depth validation, and only validate
    size if the bpp of the pixmap format is > 8.  If bpp < 8 then
    we're already protected from overflow by the width and height
    checks.
* Thu Jan 17 2008 sndirsch@suse.de
- X.Org security update
  * CVE-2007-5760 - XFree86 Misc extension out of bounds array index
  * CVE-2007-6427 - Xinput extension memory corruption.
  * CVE-2007-6428 - TOG-cup extension memory corruption.
  * CVE-2007-6429 - MIT-SHM and EVI extensions integer overflows.
  * CVE-2008-0006 - PCF Font parser buffer overflow.
* Wed Dec 12 2007 sndirsch@suse.de
- xorg-server 1.4.0.90 (prerelease of 1.4.1)
* Fri Nov 30 2007 sndirsch@suse.de
- pixman.diff
  * fixed include path for pixman.h
* Thu Nov 29 2007 sndirsch@suse.de
- remove_bogus_modeline.diff
  * remove bogus monitor modelines provided by DDC (Bug #335540)
* Tue Nov 27 2007 sndirsch@suse.de
- commit-184e571.diff
  * Adjust offsets of modes that do not fit virtual screen size.
- commit-c6c284e.diff
  * Initialize Mode with 0 in xf86RandRModeConvert.
- commit-f6401f9.diff
  * Don't segfault if referring to a relative output where no modes survived.
- commit-f7dd0c7.diff
  * Only clear crtc of output if it is the one we're actually working on.
- commit-fa19e84.diff
  * Fix initial placement of LeftOf and Above.
* Thu Nov 22 2007 sndirsch@suse.de
- pixman.diff no longer required
* Sun Nov 18 2007 sndirsch@suse.de
- s390(x): allow mfb build without Xorg server being built
* Thu Nov 15 2007 sndirsch@suse.de
- commit-29e0e18.diff
  * Make config file preferred mode override monitor preferred
    mode.
- commit-feac075.diff
  * Leave hardware-specified preferred modes alone when user
    preference exists.
- obsoletes preferred_mode-fix.diff
* Thu Nov 15 2007 sndirsch@suse.de
- added xorg-x11-fonts-core/xorg-x11 to Requires (Bug #341312)
* Wed Nov 14 2007 schwab@suse.de
- ia64linuxPciInit: allocate extra space for fake devices.
* Sat Nov 10 2007 sndirsch@suse.de
- updated to Mesa 7.0.2 (final) sources
* Wed Oct 31 2007 sndirsch@suse.de
- updated to Mesa 7.0.2 RC1 sources
* Tue Oct 23 2007 sndirsch@suse.de
- xorg-server-1.4-vnc-64bit.diff
  * fixes segfault on 64bit during Xserver start; make sure to
    define _XSERVER64 by having HAVE_DIX_CONFIG_H defined and
    therefore including dix-config.h, so Atom is CARD32 instead of
    unsigned long before and no longer messes up the pInfo structure
    in xf86rfbMouseInit/xf86rfbKeybInit
- finally enabled build of xf4vnc (standalone Xvnc and VNC Xserver
  module)
* Fri Oct 19 2007 sndirsch@suse.de
- updated xf4vnc patch; still disabled due to problematic vnc module
* Tue Oct  9 2007 sndirsch@suse.de
- preferred_mode-fix.diff
  * more reasonable patch (Bug #329724)
* Thu Oct  4 2007 sndirsch@suse.de
- preferred_mode-fix.diff
  * fixed endless loop if PreferredMode is set (Bug #329724)
* Wed Oct  3 2007 sndirsch@suse.de
- removed obsolete patch p_pci-domain.diff (Bug #308693, comment #26)
- apply p_pci-off-by-one.diff.ia64 on all platforms since it clearly
  only affects platforms, where INCLUDE_XF86_NO_DOMAIN is *not* set;
  this still not explains why we have seen Xserver hangups with the
  patch in place on at least some %%ix86/x86_64 machines with fglrx/
  nvidia driver IIRC; it needs to verified if this problem is still
  reproducable ... (Bug #308693, comment #25)
* Wed Oct  3 2007 sndirsch@suse.de
- xserver-1.3.0-xkb-and-loathing.patch
  * Ignore (not just block) SIGALRM around calls to Popen()/Pclose().
    Fixes a hang in openoffice when opening menus. (Bug #245711)
* Wed Oct  3 2007 sndirsch@suse.de
- added missing ia64Pci.h; required for IA64
* Wed Oct  3 2007 sndirsch@suse.de
- recreated p_pci-off-by-one.diff.ia64; the default fuzz factor of
  patch (2) resulted in a hunk applied to the wrong function and
  therefore broke the build :-(
* Fri Sep 28 2007 sndirsch@suse.de
- xorg-server 1.4
  * Welcome to X.Org X Server 1.4, now with hotplugging input to go
    with the hotplugging output.  Also included in this release are
    many performance and correctness fixes to the EXA acceleration
    architecture, support for DTrace profiling of the X Server,
    accelerated GLX_EXT_texture_from_pixmap with supporting DRI
    drivers, and many improvements to the RandR 1.2 support that
    was added in xorg-server-1.3. The X Server now relies on the
    pixman library, which replaces the fb/fbcompose.c and
    accelerated implementations that were previously shared through
    code-duplication with the cairo project.
  * obsolete patches:
  - bug-259290_trapfault.diff
  - cfb8-undefined.diff
  - commit-c09e68c
  - i810_dri_fix_freeze.diff
  - p_bug159532.diff
  - p_enable-altrix.diff
  - p_pci-ce-x.diff
  - p_pci-off-by-one.diff
  - p_xorg_rom_read.diff
  - randr12-2926cf1da7e4ed63573bfaecdd7e19beb3057d9b.diff
  - randr12-5b424b562eee863b11571de4cd0019cd9bc5b379.diff
  - randr12-aec0d06469a2fa7440fdd5ee03dc256a68704e77.diff
  - randr12-b2dcfbca2441ca8c561f86a78a76ab59ecbb40e4.diff
  - randr12-b4193a2eee80895c5641e77488df0e72a73a3d99.diff
  - remove__GLinterface.patch
  - support_mesa6.5.3.patch
  - use-composite-for-unequal-depths.patch
  - x86emu.diff
  - xephyr-sig11-fix.diff
  * adjusted patches:
  - 64bit.diff
  - bug-197858_dpms.diff
  - bug227111-ddc_screensize.diff
  - disable-root-xorg_conf.diff
  - fpic.diff
  - glx-align.patch
  - libdrm.diff
  - p_bug96328.diff
  - p_ia64-console.diff
  - p_vga-crashfix.diff
  - xephyr.diff
- pixman.diff:
  * search for pixman instead of pixman-1
- bumped version to 7.3
* Tue Sep 25 2007 sndirsch@suse.de
- remove wrongly prebuilt xf1bpp files after extracting tarball;
  fixes vga module loading (Bug #328201)
- do not use "make -j" to (quick)fix xf1bpp build
- do not apply p_pci-domain.diff on IA64
- use updated off-by-one patch by schwab for IA64
* Fri Sep 21 2007 sndirsch@suse.de
- edit_data_sanity_check.diff:
  * added sanity check for monitor EDID data (Bug #326454)
* Tue Sep 11 2007 sndirsch@suse.de
- reverted changes by schwab on Fri Sep 7; these resulted i a black
  screen during Xserver start with any driver on non-IA64 platforms
* Mon Sep 10 2007 sndirsch@suse.de
- use-composite-for-unequal-depths.patch:
  * Use Composite when depths don't match (Bug #309107, X.Org Bug
    [#7447])
* Fri Sep  7 2007 schwab@suse.de
- Update off-by-one patch.
- Remove empty patch.
* Mon Sep  3 2007 sndirsch@suse.de
- fbdevhw.diff:
  * ignore pixclock set to 0 by Xen kernel (Bug #285523)
* Fri Aug 31 2007 sndirsch@suse.de
- added several RANDR 1.2 fixes (Bug #306699)
  * randr12-2926cf1da7e4ed63573bfaecdd7e19beb3057d9b.diff
    Allocate the right number of entries for saving crtcs
  * randr12-5b424b562eee863b11571de4cd0019cd9bc5b379.diff
    Set the crtc before the output change is notified. Set the new
    randr crtc of the output before the output change notification
    is delivered to the clients. Remove RROutputSetCrtc as it is
    not really necessary. All we have to do is set the output's
    crtc on RRCrtcNotify
  * randr12-8d230319040f0a7f72231da2bf5ec97dc3612e21.diff
    Fix the output->crtc initialization in the old randr setup
  * randr12-aec0d06469a2fa7440fdd5ee03dc256a68704e77.diff
    Fix a crash when rotating the screen. Remember output->crtc
    before setting a NULL mode because RRCrtcNotify now sets
    output->crtc to NULL.  Use the saved crtc to set the new mode.
  * randr12-b2dcfbca2441ca8c561f86a78a76ab59ecbb40e4.diff
    RRScanOldConfig cannot use RRFirstOutput before output is
    configured. RRFirstOutput returns the first active output,
    which won't be set until after RRScanOldConfig is finished
    running. Instead, just use the first output (which is the only
    output present with an old driver, after all).
  * randr12-b4193a2eee80895c5641e77488df0e72a73a3d99.diff
    RRScanOldConfig wasn't getting crtcs set correctly. The output
    crtc is set by RRCrtcNotify, which is called at the end of
    RRScanOldConfig. Several uses of output->crtc in this function
    were wrong.
* Thu Aug 23 2007 sndirsch@suse.de
- i810_dri_fix_freeze.diff:
  * fixes freeze after pressing Ctrl-Alt-BS (X.Org Bug #10809)
* Thu Aug 23 2007 sndirsch@suse.de
- xserver-mode-fuzzy-check.diff:
  * Fix for Xserver being more fuzzy about mode validation
  (Bug #270846)
* Sat Aug 18 2007 sndirsch@suse.de
- disable AIGLX by default; without enabled Composite extension
  (still problematic on many drivers) it's rather useless anyway
- updated xorg.conf manual page
* Sat Aug 11 2007 dmueller@suse.de
- fix fileconflict over doc/MAINTAINERS
- build parallel
* Sat Aug  4 2007 sndirsch@suse.de
- updated Mesa source to bugfix release 7.0.1
* Thu Jul 19 2007 sndirsch@suse.de
- xephyr-sig11-fix.diff:
  * long vs. CARD32 mismatch in KeySym definitions between client
    and server code - this patch seems to fix it (and the input
    rework in head fixed it as well in a different way)
    (Bug #235320)
* Sat Jul 14 2007 sndirsch@suse.de
- fixed build on s390(x)
* Tue Jul  3 2007 sndirsch@suse.de
- added X(7) and security(7) manual pages
* Sat Jun 23 2007 sndirsch@suse.de
- updated Mesa source to final release 7.0
* Thu Jun 21 2007 sndirsch@suse.de
- updated Mesa source to release 7.0 RC1
  * Mesa 7.0 is a stable, follow-on release to Mesa 6.5.3. The only
    difference is bug fixes. The major version number bump is due
    to OpenGL 2.1 API support.
* Wed Jun  6 2007 sndirsch@suse.de
- simplified p_default-module-path.diff
* Tue May 22 2007 sndirsch@suse.de
- disabled build of Xprt
- moved Xdmx, Xephyr, Xnest and Xvfb to new subpackage
  xorg-x11-server-extra
* Wed May  2 2007 sndirsch@suse.de
- commit-c09e68c:
  * Paper over a crash at exit during GLX teardown
* Mon Apr 30 2007 sndirsch@suse.de
- updated to Mesa 6.5.3 sources
- obsoletes the following patches:
  * bug-211314_mesa-destroy_buffers.diff
  * bug-211314_mesa-framebuffer-counting.diff
  * bug-211314-patch-1.diff
  * bug-211314-patch-2.diff
  * bug-211314-patch-3.diff
  * bug-211314-patch-4.diff
  * bug-211314-patch-5.diff
  * bug-211314-patch-6.diff
  * bug-211314-patch-7.diff
  * bug-211314-patch-8.diff
  * bug-211314-patch-9.diff
  * bug-211314-patch-10.diff
  * bug-211314-patch-11.diff
  * bug-211314_mesa-refcount-memleak-fixes.diff
  * Mesa-6.5.2-fix_radeon_cliprect.diff
- remove__GLinterface.patch/
  support_mesa6.5.3.patch
  * required Xserver changes for Mesa 6.5.3
* Sat Apr 28 2007 sndirsch@suse.de
- xorg-x11-server-1.2.99-unbreak-domain.patch:
  * This patch fixes some multi-domain systems such as Pegasos with
    xorg-server 1.3. Since pci-rework should get merged soon and
    this patch is a bit of a hack, it never got pushed upstream.
    (X.Org Bug #7248)
* Fri Apr 27 2007 sndirsch@suse.de
- back to Mesa 6.5.2 (Bug #269155/269042)
* Wed Apr 25 2007 sndirsch@suse.de
- Mesa update: 4th RC ready
  * This fixes some breakage in RC3.
* Tue Apr 24 2007 sndirsch@suse.de
- Mesa update: 3rd release candidate
  * updated Windows/VC8 project files.
* Sun Apr 22 2007 sndirsch@suse.de
- updated to Mesa 6.5.3rc2 sources
  * a number of bug fixes since the first RC
* Sat Apr 21 2007 sndirsch@suse.de
- updated to Mesa 6.5.3rc1 sources
- obsoletes the following patches:
  * bug-211314_mesa-destroy_buffers.diff
  * bug-211314_mesa-framebuffer-counting.diff
  * bug-211314-patch-1.diff
  * bug-211314-patch-2.diff
  * bug-211314-patch-3.diff
  * bug-211314-patch-4.diff
  * bug-211314-patch-5.diff
  * bug-211314-patch-6.diff
  * bug-211314-patch-7.diff
  * bug-211314-patch-8.diff
  * bug-211314-patch-9.diff
  * bug-211314-patch-10.diff
  * bug-211314-patch-11.diff
  * bug-211314_mesa-refcount-memleak-fixes.diff
  * Mesa-6.5.2-fix_radeon_cliprect.diff
- GL-Mesa-6.5.3.diff:
  * adjusted GL subdir to Mesa 6.5.3rc1
* Fri Apr 20 2007 sndirsch@suse.de
- xserver 1.3.0.0 release
  * Syncmaster 226 monitor needs 60Hz refresh (#10545).
  * In AIGLX EnterVT processing, invoke driver EnterVT before
    resuming glx.
  * Disable CRTC when SetSingleMode has no matching mode. Update
    RandR as well.
  * Rotate screen size as needed from RandR 1.1 change requests.
  * Add quirk for Acer AL1706 monitor to force 60hz refresh.
  * RandR 1.2 spec says CRTC info contains screen-relative geometry
  * typo in built-in module log message
  * Use default screen monitor for one of the outputs.
  * Allow outputs to be explicitly enabled in config, overriding
    detect.
  * Was accidentally disabling rotation updates in mode set.
  * Disable SourceValidate in rotation to capture cursor.
* Tue Apr 10 2007 sndirsch@suse.de
- Mesa-6.5.2-fix_radeon_cliprect.diff:
  * fixes X.Org Bug #9876
* Fri Apr  6 2007 sndirsch@suse.de
- bug-259290_trapfault.diff:
  * fixes crash caused by bug in XRender code (Bug #259290)
* Fri Apr  6 2007 sndirsch@suse.de
- xserver 1.2.99.905 release:
  * CVE-2007-1003: XC-MISC Extension ProcXCMiscGetXIDList() Memory
    Corruption
  * X.Org Bug #10296: Fix timer rescheduling
- obsoletes bug-243978_xcmisc.diff
* Fri Apr  6 2007 sndirsch@suse.de
- xserver 1.2.99.904 release:
  * Don't erase current crtc for outputs on CloseScreen
* Wed Apr  4 2007 sndirsch@suse.de
- bug-243978_xcmisc.diff:
  * mem corruption in ProcXCMiscGetXIDList (CVE-2007-1003, Bug #243978)
* Wed Apr  4 2007 sndirsch@suse.de
-  bug-211314_mesa-refcount-memleak-fixes.diff:
  * Fix for memleaks and refount bugs (Bug #211314)
* Fri Mar 30 2007 sndirsch@suse.de
- p_default-module-path.diff:
  * only return /usr/%%lib/xorg/modules in "-showDefaultModulePath"
    Xserver option (Bug #257360)
- set Xserver version to 7.2.0 with configure option
  (Bugs #257360, #253702)
* Tue Mar 27 2007 sndirsch@suse.de
- xserver 1.2.99.903 release:
  * Create driver-independent CRTC-based cursor layer.
  * Allow xf86_reload_cursors during server init.
  * Don't wedge when rotating more than one CRTC.
  * Correct ref counting of RRMode structures
  * Remove extra (and wrong) I2C ByteTimeout setting in DDC code.
  * Slow down DDC I2C bus using a RiseFallTime of 20us for old
    monitors.
  * Clean up Rotate state on server reset.
  * Clear allocated RandR screen private structure.
  * Clean up xf86CrtcRec and xf86OutputRec objects at CloseScreen.
  * Make sure RandR events are delivered from RRCrtcSet.
  * Fix Pending property API, adding RRPostPendingProperty.
  * Incorrect extra memory copy in RRChangeOutputProperty.
  * Ensure that crtc desired values track most recent mode.
  * Make pending properties force mode set. And, remove
    AttachScreen calls.
  * Set version to 1.2.99.903 (1.3 RC3)
  * fbdevhw: Consolidate modeset ioctl calling, report failure if
    it modifies mode.
  * fbdevhw: Fix some issues with the previous commit.
  * fbdevhw: Use displayWidth for fbdev virtual width when
    appropriate.
  * fbdevhw: Override RGB offsets and masks after setting initial
    mode.
  * fbdevhw: Consider mode set equal to mode requested if virtual
    width is larger.
  * fbdevhw: Only deal with RGB weight if default visual is True-
    or DirectColor.
  * Add per-drawable Xv colour key helper function.
  * Bump video driver ABI version to 1.2.
* Mon Mar 19 2007 sndirsch@suse.de
- no longer apply bug-211314_mesa-context.diff,
  bug-211314_p_drawable_privclean.diff (Bug #211314, comment #114)
- added different Mesa patches (Bug #211314, comments #114/#115)
* Thu Mar 15 2007 schwab@suse.de
- Remove bug197190-ia64.diff, fix x86emu instead.
* Wed Mar 14 2007 sndirsch@suse.de
- xserver 1.2.99.902 release:
  * Xprint: shorten font filename to fit in tar length limit
  * Move xf86SetSingleMode into X server from intel driver.
  * Add xf86SetDesiredModes to apply desired modes to crtcs.
  * Use EDID data to set screen physical size at server startup.
  * Allow relative positions to use output names or monitor
    identifiers.
  * Add xf86CrtcScreenInit to share initialization across drivers.
  * Add hw/xfree86/docs/README.modes, documenting new mode setting
    APIs.
  * Remove stale monitor data when output becomes disconnected.
  * Revert "Xprint includes a filename which is too long for tar."
  * Revert "Xext: Update device's lastx/lasty when sending a motion
    event with XTest."
  * Xext: Update device's lastx/lasty when sending a motion event
    with XTest.
* Wed Mar 14 2007 sndirsch@suse.de
- xf86crtc_allowdual.diff no longer required; replaced by
  xrandr_12_newmode.diff in xrandr (xorg-x11 package)
* Wed Mar 14 2007 sndirsch@suse.de
- bug197190-ia64.diff:
  * missing -DNO_LONG_LONG for IA64 (Bug #197190)
* Fri Mar  9 2007 sndirsch@suse.de
- xf86crtc_allowdual.diff:
  * allows dualhead even when the second monitor is not yet
    connected during Xserver start
* Tue Mar  6 2007 sndirsch@suse.de
- %%post: replace "i810beta" with "intel" in existing xorg.conf
* Mon Mar  5 2007 sndirsch@suse.de
- xserver 1.2.99.901 release:
  * RandR 1.2
  * EXA damage track
  * minor fixes
* Mon Feb 19 2007 sndirsch@suse.de
- use global permissions files for SUSE > 10.1 (Bug #246228)
* Thu Feb  1 2007 sndirsch@suse.de
- improved bug-197858_dpms.diff to fix Xserver crash (Bug #197858)
* Mon Jan 29 2007 sndirsch@suse.de
- bug-197858_dpms.diff:
  * finally fixed "X server wakes up on any ACPI event" issue
    (Bug #197858)
* Thu Jan 25 2007 sndirsch@suse.de
- bug-211314_p_drawable_privclean.diff:
  * fixed for cleaning up pointers
* Wed Jan 24 2007 sndirsch@suse.de
- fixed build
* Wed Jan 24 2007 sndirsch@suse.de
- bug-211314_p_drawable_privclean.diff:
  * fixes Xserver crash in Mesa software rendering path (Bug #211314)
* Tue Jan 23 2007 sndirsch@suse.de
- xserver 1.2.0 release
  * Bug #9219: Return BadMatch when trying to name the backing
    pixmap of an unrealized window.
  * Bug #9219: Use pWin->viewable instead of pWin->realized to
    catch InputOnly windows too.
  * Fix BSF and BSR instructions in the x86 emulator.
  * Bug #9555: Always define _GNU_SOURCE in glibc environments.
  * Bug #8991: Add glXGetDrawableAttributes dispatch; fix texture
    format therein.
  * Bump video and input ABI minors.
  * Fix release date.
  * Fix syntax error in configure check for SYSV_IPC that broke
    with Sun cc
  * Map missing keycodes for Sun Type 5 keyboard on Solaris SPARC
  * Update pci.ids to 2006-12-06 from pciids.sf.net
  * Xorg & Xserver man page updates for 1.2 release
  * xorg.conf man page should say "XFree86-DGA", not "Xorg-DGA"
  * Xserver man page: remove bc, add -wr
  * Update pci.ids to 2007-01-18 snapshot
  * Update Xserver man page to match commit
    ed33c7c98ad0c542e9e2dd6caa3f84879c21dd61
  * Fix Tooltip from minimized clients
  * Fix Xming fails to use xkb bug
  * Fix bad commit
  * Set Int10Current->Tag for the linux native int10 module
  * added mipmap.c
  * configure.ac: prepare for 1.2.0 (X11R7.2)
  * sparc: don't include asm/kbio.h -- it no longer exists in
    current headers.
  * Minor typos in Xserver man page.
  * Fix several cases where optimized paths were hit when they
    shouldn't be.
  * Try dlsym(RTLD_DEFAULT) first when finding symbols.
  * Fix RENDER issues (bug #7555) and implement RENDER add/remove
    screen
  * For Xvfb, Xnest and Xprt, compile fbcmap.c with -DXFree86Server
  * Multiple integer overflows in dbe and render extensions
  * Require glproto >= 1.4.8 for GLX.
  * __glXDRIscreenProbe: Use drmOpen/CloseOnce.
  * xfree86/hurd: re-add missing keyboard support (bug #5613)
  * remove last remaning 'linux'isms (bug #5613)
- obsoletes
  * Mesa-6.5.2.diff
  * xorg-server-1.1.99.901-GetDrawableAttributes.patch
  * int10-fix.diff
  * cve-2006-6101_6102_6103.diff
- disabled build of VNC server/module
* Wed Jan 17 2007 sndirsch@suse.de
- bug-211314_mesa-context.diff:
  * fixes Xserver crash in software rendering fallback (Bug #211314)
* Tue Jan 16 2007 sndirsch@suse.de
- 0018-vnc-support.txt.diff
  * fixed unresolved symbols vncRandomBytes/deskey in VNC module
    (terminated Xserver when client connected)
* Tue Jan 16 2007 sndirsch@suse.de
- bug227111-ddc_screensize.diff:
  * allow user overrides for monitor settings (Bug #227111)
* Mon Jan 15 2007 sndirsch@suse.de
- loadmod-bug197195.diff:
  * check the complete path (Bug #197195)
* Sun Jan 14 2007 sndirsch@suse.de
- added build of VNC support (0018-vnc-support.txt/
  0018-vnc-support.txt.diff); see 0018-vnc-support.txt.mbox for
  reference
* Tue Jan  9 2007 sndirsch@suse.de
- cve-2006-6101_6102_6103.diff:
  * CVE-2006-6101 iDefense X.org ProcRenderAddGlyphs (Bug #225972)
  * CVE-2006-6102 iDefense X.org ProcDbeGetVisualInfo (Bug #225974)
  * CVE-2006-6103 iDefense X.org ProcDbeSwapBuffers (Bug #225975)
* Tue Dec 19 2006 sndirsch@suse.de
- int10-fix.diff
  * Set Int10Current->Tag for the linux native int10 module (X.Org
    Bug #9296)
  * obsoletes p_initialize-pci-tag.diff
* Tue Dec 19 2006 sndirsch@suse.de
- reverted latest change by schwab (Bug #197190, comment #67)
* Mon Dec 18 2006 schwab@suse.de
- Fix off-by-one in pci multi-domain support [#229278].
* Wed Dec 13 2006 sndirsch@suse.de
- libdrm.diff:
  * no longer fail when some driver tries to load "drm" module
* Tue Dec 12 2006 sndirsch@suse.de
- xorg-server-1.1.99.901-GetDrawableAttributes.patch:
  * hopefully fixes AIGLX issues (X.Org Bug #8991)
* Fri Dec  8 2006 sndirsch@suse.de
- another 64bit warning fix
* Sat Dec  2 2006 sndirsch@suse.de
- X.Org 7.2RC3 release
  * Add a -showDefaultModulePath option.
  * Add a -showDefaultLibPath option.
  * Add DIX_CFLAGS to util builds.
  * Fix release date, and tag 1.1.99.903
  * make X server use system libdrm - this requires libdrm >= 2.3.0
  * DRI: call drmSetServerInfo() before drmOpen().
  * add extern to struct definition
  * fixup configure.ac problems with DRI_SOURCES and LBX_SOURCES
  * bump to 1.1.99.903
  * remove CID support (bug #5553)
  * dri: setup libdrm hooks as early as possible.
  * Bug #8868: Remove drm from SUBDIRS now that the directory is gone.
  * Fix typo before the last commit.
  * Fix GL context destruction with AIGLX.
  * On DragonFLy, default to /dev/sysmouse (just like on FreeBSD).
  * ffs: handle 0 argument (bug #8968)
  * Bug #9023: Only check mice for "mouse" or "void" if identifier
    is != NULL.  Fix potential NULL pointer access in timer code.
- updated Mesa sources to 6.5.2
* Tue Nov 28 2006 sndirsch@suse.de
- xserver-timers.diff:
  * fix null pointer reference in timer code (Bug #223718)
* Mon Nov 20 2006 sndirsch@suse.de
- p_pci-off-by-one.diff:
  * readded off by one fix, which has been dropped by accident
  (Bug #197190)
* Mon Nov 20 2006 sndirsch@suse.de
- acpi_events.diff:
  * distinguish between general and input devices also for APM
    (Bug #197858)
* Tue Nov 14 2006 sndirsch@suse.de
- removed /etc/X11/Xsession.d/92xprint-xpserverlist (Bug #220733)
* Tue Nov 14 2006 sndirsch@suse.de
- mouse-fix.diff:
  * prevent driver from crashing when something different than
    "mouse" or "void" is specified; only check mice for "mouse"
    or "void" if identifier is != NULL. (X.Org Bug #9023)
* Tue Nov 14 2006 sndirsch@suse.de
- X.Org 7.2RC2 release
- adjusted p_enable-altrix.diff, p_pci-domain.diff
- obsoletes p_pci-ia64.diff, xorg-xserver-ia64-int10.diff
  p_pci-legacy-mmap.diff
- Changes in RC2 since RC1
  Aaron Plattner:
    Fix standard VESA modes.
  Adam Jackson:
    Bug #6786: Use separate defines for server's Fixes support level.
    'make dist' fixes.
    Fix distcheck.
    Include a forgotten ia64 header in the distball.  Builds on ia64 now.
    configure.ac bump.
  Alan Coopersmith:
    Make sure xorgcfg files are included even when dist made with
  - -disable-xorgcfg
    Use getisax() instead of asm code to determine available x86 ISA
    extensions on Solaris
    Pre-release message should tell users to check git, not CVS, for updates
    Fix automake error: BUILT_SOURCES was defined multiple times on Solaris
    Bug #1997: AUDIT messages should contain uid for local accesses
    If getpeerucred() is available, include pid & zoneid in audit messages
    too
    Make _POSIX_C_SOURCE hack work with Solaris headers
  Alan Hourihane:
    Small modification to blocking signals when switching modes.
  Bjorn Helgaas:
    Do not map full 0-1MB legacy range
  Bram Verweij:
    xfree86/linux acpi: fix tokenising
  Daniel Stone:
    GetTimeInMillis: spuport monotonic clock
    WaitForSomething: allow time to rewind
    Revert "WaitForSomething: allow time to rewind"
  Revert "GetTimeInMillis: spuport monotonic clock"
  add 'general socket' handler, port ACPI to use it
  WaitForSomething: allow time to rewind
  WaitForSomething: only rewind when delta is more than 250ms
  GetTimeInMillis: spuport monotonic clock
  GetTimeInMillis: simplify monotonic test
    GetTimeInMillis: use correct units for clock_gettime
    os: fix sun extensions test
  Eamon Walsh:
    Bug #8875: Security extension causes Xorg to core dump on server reset
    whitespace adjust
    More work on Bug #8875: revert previous fix and try using client
    argument
    Bug #8937: Extension setup functions not called on server resets
  Egbert Eich:
    Fixing mach64 driver bailing out on ia64
    Make int10 fully domain aware.
  Erik Andren:
    remove XFree86 changelogs (bug #7262)
  Joshua Baergen:
    Create xorg.conf.example (Gentoo bug #138623).
  Laurence Withers:
    CreateColormap: fix return value (bug #7083)
  Matthias Hopf:
    Build with -D_PC on ix86 only.
    Added missing domain stripping in already domain aware code.
    Added linux 2.6 compatible domain aware device scanning code.
    Fixing domain support for ia64
    Add domain support to linuxPciOpenFile().
    Fix device path in altixPCI.c to be domain aware.
    Fix obviously wrong boundary checks + cleanup unused vars.
  Matthieu Herrb:
    kill GNU-make'ism.
    Handle building in a separate objdir
  Michel Dänzer:
    Fix __glXDRIbindTexImage() for 32 bpp on big endian platforms.
    Fix test for Option "IgnoreABI".
  Myron Stowe:
    xfree86: re-enable chipset-specific drivers for Linux/ia64
  Rich Coe:
    CheckConnections: don't close down the server client (bug #7876)
* Thu Nov  9 2006 sndirsch@suse.de
- p_ppc_domain_workaround.diff:
  * ugly workaround for still missing domain support on ppc
    (Bug #202133)
* Sat Nov  4 2006 sndirsch@suse.de
- updated to snapshot of xserver-1.2-branch (soon to be released
  as X.Org 7.2RC2)
  * Make sure xorgcfg files are included even when dist made with
  - -disable-xorgcfg
  * Small modification to blocking signals when switching modes.
  * Use getisax() instead of asm code to determine available x86
    ISA extensions on Solaris
  * Pre-release message should tell users to check git, not CVS,
    for updates
  * Fix __glXDRIbindTexImage() for 32 bpp on big endian platforms.
  * Create xorg.conf.example (Gentoo bug #138623).
  * Fix test for Option "IgnoreABI".
    This option has plenty of potential for wasting the time of bug
    triagers without pretending it's always on.
  * kill GNU-make'ism.
  * Handle building in a separate objdir
  * Fix automake error: BUILT_SOURCES was defined multiple times on Solaris
  * Bug #1997: AUDIT messages should contain uid for local accesses
  * If getpeerucred() is available, include pid & zoneid in audit messages too
* Wed Nov  1 2006 sndirsch@suse.de
- added /etc/modprobe.d/nvidia
* Wed Oct 25 2006 sndirsch@suse.de
- xorg-xserver-ia64-int10.diff:
  * build int10 module with _PC only on %%ix86 (Bug #197190)
* Mon Oct 23 2006 sndirsch@suse.de
- added build of Xephyr; useful for debugging KDE apps (coolo)
* Tue Oct 17 2006 sndirsch@suse.de
- cfb8-undefined.diff:
  * fixes warning for undefined behaviour
* Tue Oct 17 2006 aj@suse.de
- Own /etc/X11/Xsession.d directory.
* Mon Oct 16 2006 aj@suse.de
- Use /etc/X11/Xsession.d.
* Sat Oct 14 2006 sndirsch@suse.de
- updated to X.Org 7.2RC1
* Fri Oct 13 2006 sndirsch@suse.de
- only disable AIGLX by default on SUSE <= 10.1 (Bug #197093)
- no longer fake release version for fglrx driver (Bug #198125)
* Mon Oct  9 2006 sndirsch@suse.de
- glx-align.patch:
  * reenabled -D__GLX_ALIGN64 on affected plaforms (X.Org Bug #8392)
- Fixes to p_pci-domain.diff (Bug #197572)
  * internal domain number of by one (was supposed to be a cleanup,
    but other code dependet on this semantics)
  * fixed another long-standing of-by-1 error
- p_enable-altrix.diff (Bug #197572)
  * This additional patch enables the build of the altrix detection
    routines, which have apparently not been included in Xorg 7.1
    yet. This patch needs a autoreconf -fi after application.
* Mon Sep 18 2006 sndirsch@suse.de
- updated to Mesa 6.5.1
* Wed Sep 13 2006 sndirsch@suse.de
- disable-fbblt-opt.diff:
  * Disable optimization (introduced by ajax) due to a general vesa
    driver crash later in memcpy (Bug #204324)
* Sat Sep  9 2006 sndirsch@suse.de
- removed two source files with imcompatible license from Mesa
  tarball (Bug #204110)
- added a check to specfile to make sure that these will not be
  reintroduced with the next Mesa update again (Bug #204110)
* Fri Sep  1 2006 sndirsch@suse.de
- moved xf86Parser.h,xf86Optrec.h back to /usr/include/xorg, since
  SaX2 build issues have finally been resolved by making use of
  "-iquote /usr/include/xorg -I."
* Thu Aug 31 2006 sndirsch@suse.de
- disable-root-xorg_conf.diff:
  * no longer consider to read /root/xorg.conf
* Tue Aug 29 2006 sndirsch@suse.de
- only require xorg-x11-fonts-core ('fixed' + 'cursor' fonts)
* Mon Aug 28 2006 sndirsch@suse.de
- fake release version for fglrx driver again, since using
  IgnoreABI does not help (the check for the ABI version is in the
  binary-only fglrx driver)
* Sun Aug 27 2006 sndirsch@suse.de
- added Requires: xorg-x11-driver-{input,video} (Bug #202080)
* Fri Aug 25 2006 sndirsch@suse.de
- ignore-abi.diff:
  * adds IgnoreABI option for xorg.conf (same as -ignoreABI)
- remove .la files
- no longer fake release version for fglrx driver; use the new
  IgnoreABI option instead!
* Fri Aug 25 2006 sndirsch@suse.de
- PCI/IA64 Patches (Bug #197572):
  * apply new p_pci-domain.diff (mhopf)
  * apply new p_pci-ce-x.diff (mhopf)
* Thu Aug 24 2006 sndirsch@suse.de
- PCI/IA64 Patches (Bug #197572):
  * removed p_mappciBIOS_complete.diff (already applied upstream)
  * apply p_pci-ia64.diff
  * apply p_pci-legacy-mmap.diff only for IA64 (as before)
  * disabled for now:
  - p_pci-domain.diff: still issues with it
  - p_pci-ce-x.diff: sits on top of p_pci-domain.diff
* Sun Aug 20 2006 sndirsch@suse.de
- added PCI/IA64 patches, but disabled them for now (Bug #197572)
- remove comp. symlinks in /usr/X11R6/bin for openSUSE >= 10.2
* Fri Aug 18 2006 sndirsch@suse.de
- fixed build for s390/s390x, e.g. use configure options
  - -disable-install-libxf86config
  - -disable-aiglx
  - -disable-dri
  - -disable-xorg
- changed os-name to "openSUSE" instead of "Linux" before
- fake release version for fglrx driver :-(
* Thu Aug 17 2006 sndirsch@suse.de
- xinerama-sig11.diff:
  * prevents Xserver Sig11 with broken Xinerama config (Bug #135002)
* Tue Aug 15 2006 sndirsch@suse.de
- moved /usr/%%_lib/pkgconfig/xorg-server.pc to xorg-x11-server
- added pkgconfig to Requires of xorg-x11-server
* Sat Aug 12 2006 sndirsch@suse.de
- disable-aiglx.diff:
  * disabled AIGLX by default (related to Bug #197093); enable it
    with 'Option "AIGLX" "true"' in ServerFlags section of xorg.conf
* Wed Aug  9 2006 sndirsch@suse.de
- enabled build of aiglx
* Wed Aug  9 2006 sndirsch@suse.de
- patch font path also in xorg.conf when set to /usr/lib/X11/fonts/
  or /usr/X11/lib/X11/fonts
* Tue Aug  8 2006 sndirsch@suse.de
- patch xorg.conf in %%post:
  * radeonold/radeon10b driver --> radeon driver
* Mon Aug  7 2006 sndirsch@suse.de
- added "Requires: xorg-x11-fonts" to prevent issues like
  "could not open default font 'fixed'" for any Xserver
* Mon Aug  7 2006 sndirsch@suse.de
- make sure that symlinks
    /usr/bin/X       --> /var/X11R6/bin/X
    /var/X11R6/bin/X --> /usr/bin/Xorg
  are packaged.
- p_xorg_acpi.diff:
  * fixed for archs which don't have HAVE_ACPI defined, e.g. ppc
* Mon Aug  7 2006 sndirsch@suse.de
- p_xf86Mode.diff:
  * removes wrong warning (Bug #139510)
- p_xorg_acpi.diff:
  * reconnect to acpid when acpid has been killed (Bug #148384)
- p_xkills_wrong_client.diff:
  * This patch has unveiled two other problems. One is rather
    serious as there seems to be a non-zero possibility that the
    Xserver closes the wrong connection and this closes the wrong
    client when it looks for stale sockets of clients that have
    disappeared (eich, Bug #150869)
- p_bug159532.diff:
  * X Clients can intentionally or unintenionally crash X11 by
    using composite on depth 4 pixmaps. This patch fixes this.
    (Bug #159532)
- p_xnest-ignore-getimage-errors.diff:
  * ignores the X error on GetImage in Xnest (Bug #174228,
    X.Org Bug #4411)
- p_initialize-pci-tag.diff:
  * initialize PCI tag correctly, which is used by an IA64 specific
    patch (see Bug #147261 for details); fixes Xserver crashes with
    fglrx driver - and possibly other drivers like vesa - during
    initial startup (!), VT switch and startup of second Xserver
    (SLED10 Blocker Bugs #180535, #170991, #158806)
- p_ia64-console.diff:
  * fixes MCA after start of second Xserver (Bug #177011)
* Sat Aug  5 2006 sndirsch@suse.de
- p_mouse_misc.diff:
  * fix X server crashes with synaptics driver (Bug #61702)
- pu_fixes.diff
  * Fixes not yet in the official version
- p_bug96328.diff:
  * fallback mouse device checking
- p_vga-crashfix.diff:
  * fixes vga driver crash (#133989)
- p_xorg_rom_read.diff
  * read rom in big chunks instead of byte-at-a-time (Bug #140811)
- ps_showopts.diff
  * Xserver "-showopts" option to print available driver options
    (Bug #137374)
* Sat Aug  5 2006 sndirsch@suse.de
- add /var/X11R6/bin directory for now (Bug #197188)
* Wed Aug  2 2006 sndirsch@suse.de
- fix setup line
* Mon Jul 31 2006 sndirsch@suse.de
- fixed fatal compiler warnings
* Mon Jul 31 2006 sndirsch@suse.de
- always (and only) patch xorg.conf if necessary
* Mon Jul 31 2006 sndirsch@suse.de
- update to xorg-server release 1.1.99.3
* Fri Jul 28 2006 sndirsch@suse.de
- use "-fno-strict-aliasing"
* Thu Jul 27 2006 sndirsch@suse.de
- use $RPM_OPT_FLAGS
- remove existing /usr/include/X11 symlink in %%pre
* Wed Jul 26 2006 sndirsch@suse.de
- install xf86Parser.h,xf86Optrec.h to /usr/include instead of
  /usr/include/xorg, so it is no longer necessary to specify
  "-I/usr/include/xorg" which resulted in including a wrong
  "shadow.h" (by X.Org) when building SaX2 (strange build error)
* Tue Jul 25 2006 sndirsch@suse.de
- added permissions files
* Tue Jul 25 2006 sndirsch@suse.de
- add compatibility symlink /usr/X11R6/bin/Xorg
* Fri Jul 21 2006 sndirsch@suse.de
- p_ValidatePci.diff:
  * no longer call ValidatePci() to fix i810 driver issues
    (Bug #191987)
* Thu Jul 20 2006 sndirsch@suse.de
- fixed build
* Tue Jun 27 2006 sndirsch@suse.de
- created package
