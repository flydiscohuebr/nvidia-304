#
# spec file for package dkms-nvidia
#
# Copyright (c) 2008 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.
# Please submit bugfixes or comments via bumblebee.obs@gmail.com
#
# norootforbuild
#
%define modname  nvidia
%define package_ver 304.137
%define package_name NVIDIA-Linux-x86

#define mirror1  http://download.nvidia.com/XFree86
#define mirror1  http://uk.download.nvidia.com/XFree86
%define mirror1  http://us.download.nvidia.com/XFree86


Name:    dkms-%{modname}
Summary: Installer for the graphics driver kernel module for GeForce 6xxx and newer GPUs
Version: %{package_ver}
Release: lp155.11.1
Url:     https://build.opensuse.org/project/show/home:Bumblebee-Project
Group:   System/Kernel
License: GPL-2.0+
Vendor:  The Bumblebee Project
Source0: README
Source2: 0001-disable-mtrr-4.3.patch
Source3: 0002-pud-offset-4.12.patch
Source4: 0003-nvidia-drm-pci-init-4.14.patch
Source5: 0004-timer-4.15.patch
Source6: 0005-usercopy-4.16.patch
Source7: 0006-do_gettimeofday-5.0.patch
Source8: 0007-subdirs-5.3.patch
Source9: 0008-on-each-cpu-5.3.patch
Source10: 0009-remove-drmp-5.5.patch
Source11: 0010-proc-ops-5.6.patch
Source12: 0011-kernel-5.7.0-setmemoryarray.patch
Source13: 0012-kernel5.8.patch
Source14: 0013-kernel5.9.patch
Source15: 0014-import-drm_legacy_pci_init-exit-from-src-linux-5.9.1.patch
Source16: 0015-add-static-and-nv_-prefix-to-copied-drm-legacy-bits.patch
Source17: 0016-fix-mistake.patch
Source18: 0016-vmalloc5.9.patch
Source19: 0017-patch-14-kernel-5.11.patch
Source20: 0018-kernel5.14.patch
Source21: 0019-kernel-5.16.patch
Source22: 0020-kernel-5.17.patch
Source23: 0021-kernel-5.18-opensusedit.patch
Source24: 0022-kernel-6.0-opensusedit.patch
Source25: 0023-kernel-6.2.patch
Source26: 0024-kernel-6.3.patch
Source27: 0025-kernel-6.5.patch
Source28: 0026-gcc14-fix.patch
Source1000: %{name}-rpmlintrc
%if 0%{?suse_version}
Conflicts: nvidia-kmp-default
Conflicts: nvidia-kmp-desktop
Conflicts: nvidia-kmp-pae
Conflicts: nvidia-kmp-xen
Conflicts: nvidia-kmp
Conflicts: nvidia-gfxG02-kmp-default
Conflicts: nvidia-gfxG02-kmp-desktop
Conflicts: nvidia-gfxG02-kmp-pae
Conflicts: nvidia-gfxG02-kmp-xen
Conflicts: nvidia-gfxG02-kmp
%endif
Provides:  nvidia-kernel-module = %{version}-%{release}
Requires:  wget binutils gcc make patch
%if 0%{?mdkversion}
Requires:  dkms-minimal
%else
Requires:  dkms
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-build


%description
This package will download and install the proprietary NVIDIA
Accelerated Linux Graphics Driver that brings accelerated 2D functionality
and high-performance OpenGL support to Linux x86 with the
use of NVIDIA graphics processing units (GPUs).

These drivers provide optimized hardware acceleration for OpenGL and X
applications and support nearly all recent NVIDIA GPU products
(see README.txt, Appendix A for a complete list of supported GPUs).
TwinView, TV-Out and flat panel displays are also supported.

http://www.nvidia.com


%prep
%if %{undefined package_name}
%{error:%%package_name missing in the Project Config}
exit -1
%endif
%if %{undefined package_ver}
%{error:%%package_ver missing in the Project Config}
exit -1
%endif
cp %SOURCE0 .
cp %SOURCE2 .
cp %SOURCE3 .
cp %SOURCE4 .
cp %SOURCE5 .
cp %SOURCE6 .
cp %SOURCE7 .
cp %SOURCE8 .
cp %SOURCE9 .
cp %SOURCE10 .
cp %SOURCE11 .
cp %SOURCE12 .
cp %SOURCE13 .
cp %SOURCE14 .
cp %SOURCE15 .
cp %SOURCE16 .
cp %SOURCE17 .
cp %SOURCE18 .
cp %SOURCE19 .
cp %SOURCE20 .
cp %SOURCE21 .
cp %SOURCE22 .
cp %SOURCE23 .
cp %SOURCE24 .
cp %SOURCE25 .
cp %SOURCE26 .
cp %SOURCE27 .
cp %SOURCE28 .



%build


%install
install -d 755 %{buildroot}/etc/modprobe.d
echo "blacklist nouveau" > %{buildroot}/etc/modprobe.d/50-blacklist-nouveau.conf


%pre
pushd /usr/src >/dev/null 2>&1
#
#	Get the nVidia package and unpack
#
%ifarch x86_64
NV_NAME=%{package_name}_64-%{version}
#
if [ -x /usr/bin/wget ] && [ ! -f $NV_NAME.run ] ; then
    #
    # Get the package
    #
    wget %{mirror1}/Linux-x86_64/%{version}/$NV_NAME.run || { rm -f $NV_NAME.run ; exit -1 ; }
fi
%else
NV_NAME=%{package_name}-%{version}
#
if [ -x /usr/bin/wget ] && [ ! -f $NV_NAME.run ] ; then
    #
    # Get the package
    #
    wget %{mirror1}/Linux-x86/%{version}/$NV_NAME.run || { rm -f $NV_NAME.run ; exit -1 ; }
EOF
fi
%endif
#
if [ -f $NV_NAME.run ] ; then
	#
	#	Check the nVidia package
	#
	sh $NV_NAME.run --check || { rm -f $NV_NAME.run ; exit -2 ; }
fi
#
if [ ! -d $NV_NAME ] && [ -f $NV_NAME.run ] ; then
	#
	#	Unpack
	#
	sh $NV_NAME.run -x || { rm -f $NV_NAME.run ; exit -3 ; }
fi
#    
NV_USAGE_FILE=/usr/src/$NV_NAME.usage
#
NV_USED=0
touch $NV_USAGE_FILE
source $NV_USAGE_FILE
NV_USED=$((NV_USED + 1))
echo "NV_USED=$NV_USED" > $NV_USAGE_FILE
#
popd >/dev/null 2>&1


%post
pushd /usr/src >/dev/null 2>&1
#
%ifarch x86_64
NV_NAME=%{package_name}_64-%{version}
%else
NV_NAME=%{package_name}-%{version}
%endif
#
MAJOR_VER=$( echo %{version} | cut -d '.' -f 1 )
MINOR_VER=$( echo %{version} | cut -d '.' -f 2 )
PATCH_VER=$( echo %{version} | cut -d '.' -f 3 )
#
if [ -d $NV_NAME ] ; then
	#
	#	Install dkms sources
	#
	rm -rf /usr/src/%{modname}-%{version}-%{release}
	mkdir -p /usr/src/%{modname}-%{version}-%{release}
	cp -R $NV_NAME/kernel/* /usr/src/%{modname}-%{version}-%{release}/
	cp -R $NV_NAME/LICENSE /usr/src/%{modname}-%{version}-%{release}/
	cp -R $NV_NAME/README.txt /usr/src/%{modname}-%{version}-%{release}/
	pushd /usr/src/%{modname}-%{version}-%{release} >/dev/null 2>&1
	echo "nvidia.ko external" > Module.supported
	#
	#	Kernel patch
	#
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0001-disable-mtrr-4.3.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0002-pud-offset-4.12.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0003-nvidia-drm-pci-init-4.14.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0004-timer-4.15.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0005-usercopy-4.16.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0006-do_gettimeofday-5.0.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0007-subdirs-5.3.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0008-on-each-cpu-5.3.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0009-remove-drmp-5.5.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0010-proc-ops-5.6.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0011-kernel-5.7.0-setmemoryarray.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0012-kernel5.8.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0013-kernel5.9.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0014-import-drm_legacy_pci_init-exit-from-src-linux-5.9.1.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0015-add-static-and-nv_-prefix-to-copied-drm-legacy-bits.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0016-fix-mistake.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0016-vmalloc5.9.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0017-patch-14-kernel-5.11.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0018-kernel5.14.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0019-kernel-5.16.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0020-kernel-5.17.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0021-kernel-5.18-opensusedit.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0022-kernel-6.0-opensusedit.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0023-kernel-6.2.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0024-kernel-6.3.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0025-kernel-6.5.patch
	patch -p1 -l < /usr/share/doc/packages/dkms-nvidia/0026-gcc14-fix.patch
	popd >/dev/null 2>&1
	#
	#	Setup dkms.conf
	#
	cat > /usr/src/%{modname}-%{version}-%{release}/dkms.conf << EOF
PACKAGE_NAME=%{modname}
PACKAGE_VERSION=%{version}-%{release}
MAKE[0]="make module KERNEL_UNAME=\${kernelver}"
CLEAN="make clean"
DEST_MODULE_LOCATION[0]="/updates/"
BUILT_MODULE_NAME[0]=%{modname}
AUTOINSTALL="yes"
NO_WEAK_MODULES="yes"
EOF
fi
#
if [ -x /usr/sbin/dkms ] ; then
	/usr/sbin/dkms add -m %{modname} -v %{version}-%{release} --rpm_safe_upgrade
	/usr/sbin/dkms build -m %{modname} -v %{version}-%{release}
	/usr/sbin/dkms install --force -m %{modname} -v %{version}-%{release}
fi
#
popd >/dev/null 2>&1

#possible fix /dev/nvidiactl permission
mkdir -p /run/udev/static_node-tags/uaccess
mkdir -p /usr/lib/tmpfiles.d
ln -snf /dev/nvidiactl /run/udev/static_node-tags/uaccess/nvidiactl 
cat >  /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G02.conf << EOF
L /run/udev/static_node-tags/uaccess/nvidiactl - - - - /dev/nvidiactl
EOF
devid=-1
for dev in $(ls -d /sys/bus/pci/devices/*); do 
  vendorid=$(cat $dev/vendor)
  if [ "$vendorid" == "0x10de" ]; then 
    class=$(cat $dev/class)
    classid=${class%%00}
    if [ "$classid" == "0x0300" -o "$classid" == "0x0302" ]; then 
      devid=$((devid+1))
      ln -snf /dev/nvidia${devid} /run/udev/static_node-tags/uaccess/nvidia${devid}
      echo "L /run/udev/static_node-tags/uaccess/nvidia${devid} - - - - /dev/nvidia${devid}" >> /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G02.conf
    fi
  fi
done
if [ "$1" = 0 ] ; then
    rm -f /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G02.conf
fi

%preun
#
#	Remove the module, rmmod can fail
#
if [ -x /sbin/rmmod ] ; then
	/sbin/rmmod %{modname} >/dev/null 2>&1
fi
#
#	Remove the module from dkms
#
if [ -x /usr/sbin/dkms ] ; then
	/usr/sbin/dkms remove -m %{modname} -v %{version}-%{release} --all --rpm_safe_upgrade || :
fi


%postun
%ifarch x86_64
NV_NAME=%{package_name}_64-%{version}
%else
NV_NAME=%{package_name}-%{version}
%endif
#
[ -d /usr/src/%{modname}-%{version}-%{release} ] && rm -rf /usr/src/%{modname}-%{version}-%{release}
#    
NV_USAGE_FILE=/usr/src/$NV_NAME.usage
#
NV_USED=1
touch $NV_USAGE_FILE
source $NV_USAGE_FILE
NV_USED=$((NV_USED - 1))
echo "NV_USED=$NV_USED" > $NV_USAGE_FILE
if [ $NV_USED == 0 ] ; then
    #
    #	Remove the sources
    #
    [ -d /usr/src/$NV_NAME ] && rm -rf /usr/src/$NV_NAME
    [ -f /usr/src/$NV_NAME.run ] && rm -f /usr/src/$NV_NAME.run
    [ -f /usr/src/$NV_NAME.usage ] && rm -f /usr/src/$NV_NAME.usage
fi


%clean
rm -rf %{buildroot}


%files
%defattr(-, root, root)
%doc README 0001-disable-mtrr-4.3.patch 0002-pud-offset-4.12.patch 0003-nvidia-drm-pci-init-4.14.patch 0004-timer-4.15.patch 0005-usercopy-4.16.patch 0006-do_gettimeofday-5.0.patch 0007-subdirs-5.3.patch 0008-on-each-cpu-5.3.patch 0009-remove-drmp-5.5.patch 0010-proc-ops-5.6.patch 0011-kernel-5.7.0-setmemoryarray.patch 0012-kernel5.8.patch 0013-kernel5.9.patch 0014-import-drm_legacy_pci_init-exit-from-src-linux-5.9.1.patch 0015-add-static-and-nv_-prefix-to-copied-drm-legacy-bits.patch 0016-fix-mistake.patch 0016-vmalloc5.9.patch 0017-patch-14-kernel-5.11.patch 0018-kernel5.14.patch 0019-kernel-5.16.patch 0020-kernel-5.17.patch 0021-kernel-5.18-opensusedit.patch 0022-kernel-6.0-opensusedit.patch 0023-kernel-6.2.patch 0024-kernel-6.3.patch 0025-kernel-6.5.patch 0026-gcc14-fix.patch
%dir /etc/modprobe.d
%config /etc/modprobe.d/50-blacklist-nouveau.conf


%changelog
* Fri Jun 14 2019 bumblebee.obs@gmail.com
- Update to 340.108
  * Updated the nvidia-drm kernel module for compatibility with the
  removal of the DRIVER_PRIME flag in recent Linux kernel versions.
  * Updated nvidia-bug-report.sh to search the systemd journal for
  gdm-x-session logs.
  * Fixed a bug that could prevent nvidia-xconfig from disabling
  the X Composite extension on version 1.20 of the X.org X server.
  * Added support to nvidia-installer for systems which provide
  ncurses libraries supporting the ncurses widechar ABI only.
  * Updated nvidia-installer to avoid problems with commands whose
  proper functionality may be dependent on system localization
  (e.g. via the LANG environment variable.) For example, some
  kernel configurations may produce unusable kernel modules if
  LANG is set to a language other than English.
  * Updated nvidia-installer for better compatibility with ncurses
  when libncurses.so.6 exposes the ncurses reentrant ABI, such as
  on openSUSE Leap 15 and SUSE Linux Enterprise 15.
  * Fixed a build failure, "too many arguments to function
  'get_user_pages'", when building the NVIDIA kernel module for
  Linux kernel v4.4.168.
  * Fixed a build failure, "implicit declaration of function
  do_gettimeofday", when building the NVIDIA kernel module for
  Linux kernel 5.0 release candidates.
* Thu Mar 28 2019 AndrewNovikov@yandex.ru
  * Fix building for Linux-5.0
  The patch by Alberto Milone, NVIDIA driver maintainer for Ubuntu
* Tue Aug 21 2018 bumblebee.obs@gmail.com
- Update to 340.107
  * Updated nvidia-installer in the 340.xx legacy driver series
  to default to installing the driver without the NVIDIA
  Unified Memory kernel module if this module fails to build at
  installation time. The 340.xx legacy Unified Memory kernel module
  is incompatible with recent Linux kernels, and the GPU hardware
  generations that the 340.xx legacy driver series is intended to
  support do not support Unified Memory.
  * Added support for X.Org xserver ABI 24 (xorg-server 1.20).
  * Improved nvidia-bug-report.sh to check for kern.log which is
  the default kernel log-file location for many Debian-based
  Linux distributions.
  * Fixed a bug which could cause X servers that export a Video\
  Driver ABI earlier than 0.8 to crash when running X11
  applications which call XRenderAddTraps().
* Tue Aug 21 2018 bumblebee.obs@gmail.com
- Update to 340.107
  * Updated nvidia-installer in the 340.xx legacy driver series
  to default to installing the driver without the NVIDIA
  Unified Memory kernel module if this module fails to build at
  installation time. The 340.xx legacy Unified Memory kernel module
  is incompatible with recent Linux kernels, and the GPU hardware
  generations that the 340.xx legacy driver series is intended to
  support do not support Unified Memory.
  * Added support for X.Org xserver ABI 24 (xorg-server 1.20).
  * Improved nvidia-bug-report.sh to check for kern.log which is
  the default kernel log-file location for many Debian-based
  Linux distributions.
  * Fixed a bug which could cause X servers that export a Video\
  Driver ABI earlier than 0.8 to crash when running X11
  applications which call XRenderAddTraps().
* Sun May  6 2018 bumblebee.obs@gmail.com
- Update to 340.106
  * Fixed a compatibility problem between the nvidia.ko's
  Page Attribute Table (PAT) support and the kernel
  Page Table Isolation (PTI) patches.
    To optimize stores to memory, nvidia.ko contains support
    for configuring the CPU's PAT registers, as a fallback for
    Linux kernels that predate kernel native PAT support.  On any
    recent kernel with CONFIG_X86_PAT enabled, the driver will
    detect that setup has already been done and skip its PAT setup.
    However, a static inline function called by nvidia.ko's
    PAT fallback support was updated in the PTI patches to use
    the EXPORT_SYMBOL_GPL symbol 'cpu_tlbstate'. nvidia.ko was
    updated to only contain its PAT fallback support, at build
    time, on kernels without CONFIG_X86_PAT.
* Wed Sep 20 2017 bumblebee.obs@gmail.com
- Update to 340.104
  * Improved compatibility with recent Linux kernels.
  * Updated nvidia-installer to label kernel modules with SELinux
  file type 'modules_object_t'. Some system SELinux policies only
  permit loading of kernel modules with this SELinux file type.
  * Removed support for checking for and downloading updated driver
  packages and precompiled kernel interfaces from nvidia-installer.
  This functionality was limited to unencrypted ftp and http,
  and was implemented using code that is no longer
  actively maintained.
* Sun Mar 12 2017 bumblebee.obs@gmail.com
- Update to 340.102
  * Added support for X.Org xserver ABI 23 (xorg-server 1.19)
  * Fixed a bug that allowed nvidia-installer to attempt loading
  kernel modules that were built against non-running kernels.
* Thu Feb  2 2017 bumblebee.obs@gmail.com
- Update to 340.101
  * Added support for X.Org xserver ABI 23 (xorg-server 1.19)
  * Fixed a bug that allowed nvidia-installer to attempt loading kernel
  modules that were built against non-running kernels.
* Fri Oct  7 2016 bumblebee.obs@gmail.com
- Update to 340.98
  * Added support for the screen_info.ext_lfb_base field, on kernels
  that have it, in order to properly handle UEFI framebuffer consoles
  with physical addresses above 4GB.
* Wed Sep  7 2016 bumblebee.obs@gmail.com
- Update to 340.96
  * Fixed a bug that could cause texture corruption in some OpenGL
  applications when video memory is exhausted by a combination of
  simultaneously running graphical and compute workloads.
  * Added support for X.Org xserver ABI 20 (xorg-server 1.18).
* Tue Feb 10 2015 bumblebee.obs@gmail.com
- Update to 340.76
  * Fixed a bug that caused frequent AMD-Vi page faults on systems with
    some AMD 8xx/9xx-series chipsets when used with some NVIDIA GPUs.
  * Fixed a regression that could cause system crashes when terminating
    the X server on systems with an NVIDIA Quadro SDI Capture card installed.
  * Fixed a bug that caused audio over HDMI to not work on some GPUs while
    using a display that supports HDMI 3D.
* Tue Dec 23 2014 bumblebee.obs@gmail.com
- Update to 340.65
  * Added support for X.Org xserver ABI 19 (xorg-server 1.17).
  * Improved compatibility with recent Linux kernels.
  * Fixed a bug that prevented internal 4K panels on some laptops
    from being driven at a sufficient bandwidth to support their
    native resolutions.
  * Fixed a regression that prevented the NVIDIA kernel module from
    loading in some virtualized environments such as Amazon Web Services.
  * Fixed a regression that caused displays to be detected incorrectly
    on some notebook systems.
  * Fixed a bug that could cause X to freeze when using Base Mosaic.
  * Fixed a regression that prevented the NVIDIA X driver from recognizing
    Base Mosaic layouts generated by the nvidia-settings control panel.
* Tue Dec 23 2014 bumblebee.obs@gmail.com
- Update to 340.58
  * Added support for the following GPUs:
    GeForce GT820M
    GeForce GTX 760A
    GeForce GTX 850A
    GeForce 810A
    GeForce 820A
    GeForce 840A
  * Fixed a bug that could cause VT-switching to fail following a
    suspend, resume, and driver reload sequence.
  * Fixed a bug that caused incorrect colors to be displayed on
    X screens running at depth 8 on some GPUs.
  * Fixed a bug that prevented GPUs from being correctly recognized
    in MetaMode strings when identified by UUID.
  * Implemented support for disabling indirect GLX context creation using
    the -iglx option available on X.Org server release 1.16 and newer.
    Note that future X.Org server releases may make the -iglx option the default.
    To re-enable support for indirect GLX on such servers, use the +iglx option.
  * Added the "AllowIndirectGLXProtocol" X config option. This option can
    be used to disallow use of GLX protocol. See "Appendix B. X Config Options"
    in the README for more details.
* Mon Oct 20 2014 bumblebee.obs@gmail.com
- Update to 340.46
  * Fixed an OpenGL issue that could cause glReadPixels() operations to be
    improperly clipped when resizing composited application windows,
    potentially leading to momentary X freezes.
  * Fixed a bug that could prevent the GLSL compiler from correctly
    evaluating some expressions when compiling shaders.
  * Fixed a bug that could cause nvidia-installer to crash while attempting to
    run nvidia-xconfig on systems where that utility is missing.
  * Added option UseSysmemPixmapAccel to control the use of GPU acceleration
    for X drawing operations on pixmaps allocated in system memory.
* Mon Sep  1 2014 bumblebee.obs@gmail.com
- Update to 340.32
  * Added support for the following GPUs:
    Quadro K420
    Quadro K620
    Quadro K2200
    Quadro K4200
    Quadro K5200
  * Fixed a regression that prevented the internal stereo infrared
  emitter built into some 3D Vision monitors from working.
  * Fixed a bug that could cause some Java-based OpenGL applications
  using JOGL to crash on startup on systems with Xinerama enabled.
  * Fixed a bug that could prevent OpenGL Framebuffer Objects (FBOs) from
  being properly redrawn after a modeswitch.
  * Fixed a memory leak that occurred when starting OpenGL applications.
  * Fixed a bug that prevented the EDID-Like Data (ELD) of audio-capable
  displays from being updated when hotplugged/unplugged.
  * Fixed a bug that caused Xid errors when using stereo mode 12 (HDMI 3D)
  on Quadro boards without an onboard stereo DIN connector.
  * Fixed a video corruption issue for VDPAU decoding of VC-1 and WMV video
  streams utilizing range remapping on Maxwell GPUs.
  * Fixed a "black window" bug in Ubuntu 14.04 when using the Xinerama and
  Composite extensions.
  * Fixed a bug that caused the screen's contents to be shifted downward
  when a G-SYNC monitor is unplugged and replaced by a non-G-SYNC monitor.
  * Fixed a bug that prevented G-SYNC from working when a G-SYNC monitor
  was unplugged and plugged back in without a modeset.
* Fri Aug  8 2014 bumblebee.obs@gmail.com
- Update to 340.24
  * Fixed a bug that prevented 3D Vision stereo and ultra low motion
  blur modes from working on G-SYNC capable monitors in some cases.
  * Fixed a bug that caused the "Allow G-SYNC" checkbox to be displayed
  in nvidia-settings even if the GPUs in the system are not
    capable of G-SYNC.
  * Fixed a kernel crash when running some applications with
  IOMMU functionality enabled.
  * Fixed a floating point exception in the OpenGL driver when
  running "Risk of Rain" under Wine.
  * Made various improvements and corrections to the information reported
  to GL applications via the KHR_debug and ARB_debug_output extensions.
  * Fixed a bug that caused GLX applications which simultaneously create
  drawables on multiple X servers to crash when swapping buffers.
  * Updated nvidia-settings to report all valid names for each target when
  querying target types, e.g. `nvidia-settings -q gpus`.
  * Added support for controlling the availability of
  Fast Approximate Antialiasing (FXAA) on a per-application basis via the
    new __GL_ALLOW_FXAA_USAGE environment variable and the corresponding
    GLAllowFXAAUsage application profile key. See the README for details.
  * Fixed a bug where indirect rendering could become corrupted on system
  configurations that disallow writing to executable memory.
  * Updated the nvidia-settings Makefiles to allow nvidia-settings to be
  dynamically linked against the host system's libjansson. This option
    can be enabled by setting the NV_USE_BUNDLED_LIBJANSSON Makefile variable
    to 0.Please note that nvidia-settings requires libjansson version 2.2 or later.
  * Removed the runlevel check from nvidia-installer: the installation
  problems formerly associated with runlevel 1 no longer apply.
  * Added initial support for G-SYNC monitors.Additional details and system
  requirements can be found at:
    http://www.geforce.com/hardware/technology/g-sync
  * Improved support for running the NVIDIA driver in configurations where
  writing to executable memory is disallowed.Driver optimizations that require
    writing to executable memory can be forcefully disabled using the new
    GL_WRITE_TEXT_SECTION environment variable.See the README for more details.
  * Fixed an X driver bug that caused gamma ramp updates of the green channel
  at depth 15, on some recent GPUs, to be ignored.
  * Fixed a regression, introduced in the 340.17 public beta release, that
  caused the NVIDIA X driver to access freed memory when exiting a
    GLX application that used either of the GLX_NV_video_out or
    GLX_NV_present_video extensions.
* Fri Jun 13 2014 bumblebee.obs@gmail.com
- Update to 340.17
  * Made various improvements and corrections to the information
    reported to GL applications via the KHR_debug and
    ARB_debug_output extensions.
  * Fixed a bug that caused GLX applications which simultaneously
    create drawables on multiple X servers to crash when swapping buffers.
  * Updated nvidia-settings to report all valid names for each target
    when querying target types, e.g. `nvidia-settings -q gpus`.
  * Added support for controlling the availability of
    Fast Approximate Antialiasing (FXAA) on a per-application basis via
    the new __GL_ALLOW_FXAA_USAGE environment variable and
    the corresponding GLAllowFXAAUsage application profile key.
    See the README for details.
  * Fixed a bug where indirect rendering could become corrupted on system
    configurations that disallow writing to executable memory.
  * Updated the nvidia-settings Makefiles to allow nvidia-settings to be
    dynamically linked against the host system's libjansson. This option
    can be enabled by setting the NV_USE_BUNDLED_LIBJANSSON Makefile
    variable to 0.  Please note that nvidia-settings requires libjansson
    version 2.2 or later.
  * Removed the runlevel check from nvidia-installer: the installation
    problems formerly associated with runlevel 1 no longer apply.
  * Added initial support for G-SYNC monitors. Additional details and
    system requirements can be found at:
    http://www.geforce.com/hardware/technology/g-sync
  * Improved support for running the NVIDIA driver in configurations where
    writing to executable memory is disallowed.  Driver optimizations that
    require writing to executable memory can be forcefully disabled using
    the new __GL_WRITE_TEXT_SECTION environment variable.  See the
    README for more details.
  * Fixed an X driver bug that caused gamma ramp updates of the green
    channel at depth 15, on some recent GPUs, to be ignored.
* Fri Jun 13 2014 bumblebee.obs@gmail.com
- Update to 337.25
  * Added support for the following GPUs:
    GeForce GTX TITAN Z
    GeForce GT 740
    GeForce 830M
    GeForce 840M
    GeForce 845M
    GeForce GTX 850M
  * Fixed a bug that caused X to crash when querying clock
    offsets for non-existent performance levels.
  * Fixed a performance regression when running KDE with desktop
    effects using the OpenGL compositing backend.
  * Fixed a bug that caused duplicate entries to appear in some
    dropdown menus in the "Application Profiles" page of nvidia-settings.
  * Fixed a regression that could cause OpenGL rendering corruption
    on X screens with 30 bit per pixel color.
  * Fixed a bug causing mode validation to fail for 4K resolutions over
    HDMI in certain situations.
  * Added nvidia-settings command line controls for over- and
    under-clocking attributes.  Please see the nvidia-settings(1) manual
    page for more details.
  * Fixed several cosmetic issues in the clock control user interface of
    nvidia-settings.
  * Added support for the GLX_EXT_stereo_tree extension.  For more details,
    see the extension specification:
    http://www.opengl.org/registry/specs/EXT/glx_stereo_tree.txt
  * Enabled support for using Unified Back Buffer (UBB) and 3D Stereo with
    the composite extension on Quadro cards.  Using stereo with a composite
    manager requires a stereo-aware composite manager.  Otherwise, only
    the left eye of stereo applications will be displayed.  See
    the GLX_EXT_stereo_tree extension specification for more details.
  * Fixed a bug that could cause OpenGL programs to freeze under some low
    memory conditions.
  * Updated the display configuration page in nvidia-settings to uniquely
    identify DisplayPort 1.2 monitors by displaying the monitor GUIDs.
  * Fixed a bug that could cause ECC settings to be displayed incorrectly
    in nvidia-settings when changing ECC settings on a multi-GPU system.
  * Removed the "OnDemandVBlankInterrupts" X configuration option: this
    option has been enabled by default since version 177.68 of
    the NVIDIA Unix driver, and the documentation had not been updated to
    reflect the new default value.
  * Fixed a bug that caused GPU errors when hotplugging daisy-chained
    DisplayPort 1.2 displays.
  * Updated the color correction settings page in the nvidia-settings
    control panel to reflect gamma changes made by other RandR clients
    while the control panel was already running.
  * Fixed a bug that prevented the use of multiple simultaneous
    X servers on UEFI systems.
  * Updated the nvidia-settings source package to build libXNVCtrl when
    building nvidia-settings, instead of relying on a pre-built library.
  * Added the ability to over- and under-clock certain GeForce GPUs in
    the GeForce GTX 400 series and later.  For GPUs that allow it, an
    offset can be applied to clock values in some clock domains of
    some performance levels.  This clock manipulation is done at the
    user's own risk.  See the README documentation of
    the "CoolBits" X configuration option for more details.
  * Updated the minimum required version of GTK+ from 2.2 to 2.4 for
    nvidia-settings.
  * Renamed the RandR output property _GUID to GUID now that it is
    an official property documented in randrproto.txt:
    http://cgit.freedesktop.org/xorg/proto/randrproto
    /commit/?id=19fc4c5a72eb9919d720ad66734029d9f8e313b1
  * Reduced CPU utilization and GPU memory utilization of
    the NVIDIA EGL driver.
  * Added support for the following EGL extensions:
  - EGL_EXT_buffer_age;
  - EGL_EXT_client_extensions;
  - EGL_EXT_platform_base;
  - EGL_EXT_platform_x11.
  * Renamed the "Clone" setting of the "MetaModeOrientation"
    X configuration option to "SamePositionAs", to make clear that
    this setting applies to the position only, and not to the resolution
    of modes in the MetaMode.
  * Added NV-CONTROL attribute NV_CTRL_VIDEO_ENCODER_UTILIZATION to
    query utilization percentage of the video encoder engine.
  * Added support for the GLX_NV_delay_before_swap extension.  For more
    details, see the extension specification:
    http://www.opengl.org/registry/specs/NV/glx_delay_before_swap.txt
  * Report correct buffer sizes for RGB GLX visuals, GLXFBConfigs,
    and EGLConfigs.  Previously, RGB10 and RGB8 formats were reported as
    having 32 bits, and RGB5 formats were reported as having 16 bits.
    Now they are correctly reported as 30, 24, and 15 bit formats
    respectively as required by the GLX and EGL specifications.
* Sun May 11 2014 bumblebee.obs@gmail.com
- Update to 337.19
  * Fixed a bug causing mode validation to fail for 4K resolutions
  over HDMI in certain situations.
  * Added nvidia-settings command line controls for over- and
  under-clocking attributes. Please see the nvidia-settings(1) manual
    page for more details.
  * Fixed several cosmetic issues in the clock control user interface
  of nvidia-settings.
  * Added support for the GLX_EXT_stereo_tree extension. For more details,
  see the extension specification:
    http://www.opengl.org/registry/specs/EXT/glx_stereo_tree.txt
  * Enabled support for using Unified Back Buffer (UBB) and 3D Stereo
  with the composite extension on Quadro cards. Using stereo with
    a composite manager requires a stereo-aware composite manager.
    Otherwise, only the left eye of stereo applications will be displayed.
    See the GLX_EXT_stereo_tree extension specification for more details.
  * Fixed a bug that caused blank screens and flickering when rotating
  displays in a Base Mosaic layout.
  * Fixed a bug that caused BadRRCrtc or BadRROutput errors for
  big-endian X11 clients making certain XRandR requests.
  * Fixed a bug that corrupted certain software rendering, notably
  the stippled text used to represent disabled entries in
    xterm's pop-up menus.
  * Fixed a bug that caused corruption or blank screens on monitors that
  use EDID version 1.3 or older when they are connected via
    DisplayPort on graphics boards that use external DisplayPort encoders,
    such as the Quadro FX 4800.
* Thu Apr 10 2014 bumblebee.obs@gmail.com
- Update to 337.12
  * Added support for the following GPUs:
    GeForce 830M
    GeForce 840M
    GeForce 845M
    GeForce GTX 850M
    GeForce GTX 860M
    GeForce GTX 870M
    GeForce GTX 880M
    GeForce GT 705
    GeForce GT 720
  * Fixed a bug that could cause OpenGL programs to freeze under some low
    memory conditions.
  * Updated the display configuration page in nvidia-settings to uniquely
    identify DisplayPort 1.2 monitors by displaying the monitor GUIDs.
  * Fixed a bug that could cause ECC settings to be displayed incorrectly
    in nvidia-settings when changing ECC settings on a multi-GPU system.
  * Removed the "OnDemandVBlankInterrupts" X configuration option: this
    option has been enabled by default since version 177.68 of the NVIDIA
    Unix driver, and the documentation had not been updated to reflect
    the new default value.
  * Fixed a bug that caused GPU errors when hotplugging daisy-chained
    DisplayPort 1.2 displays.
  * Updated the color correction settings page in the nvidia-settings
    control panel to reflect gamma changes made by other RandR clients
    while the control panel was already running.
  * Fixed a bug that prevented the use of multiple simultaneous X servers
    on UEFI systems.
  * Updated the nvidia-settings source package to build libXNVCtrl when
    building nvidia-settings, instead of relying on a pre-built library.
  * Added the ability to over- and under-clock certain GeForce GPUs in
    the GeForce GTX 400 series and later.  For GPUs that allow it, an
    offset can be applied to clock values in some clock domains of some
    performance levels.  This clock manipulation is done at the user's
    own risk.  See the README documentation of the "CoolBits"
    X configuration option for more details.
  * Updated the minimum required version of GTK+ from 2.2 to 2.4 for
    nvidia-settings.
  * Renamed the RandR output property _GUID to GUID now that it is an
    official property documented in randrproto.txt:
    http://cgit.freedesktop.org/xorg/proto/randrproto/
    commit/?id=19fc4c5a72eb9919d720ad66734029d9f8e313b1
  * Reduced CPU utilization and GPU memory utilization of the
    NVIDIA EGL driver.
  * Added support for the following EGL extensions:
  - EGL_EXT_buffer_age;
  - EGL_EXT_client_extensions;
  - EGL_EXT_platform_base;
  - EGL_EXT_platform_x11.
  * Renamed the "Clone" setting of the "MetaModeOrientation"
    X configuration option to "SamePositionAs", to make clear that this
    setting applies to the position only, and not to the resolution of
    modes in the MetaMode.
  * Added NV-CONTROL attribute NV_CTRL_VIDEO_ENCODER_UTILIZATION to query
    utilization percentage of the video encoder engine.
  * Added support for the GLX_NV_delay_before_swap extension.  For more
    details, see the extension specification:
    http://www.opengl.org/registry/specs/NV/glx_delay_before_swap.txt
  * Report correct buffer sizes for RGB GLX visuals, GLXFBConfigs, and
    EGLConfigs.  Previously, RGB10 and RGB8 formats were reported as
    having 32 bits, and RGB5 formats were reported as having 16 bits.
    Now they are correctly reported as 30, 24, and 15 bit formats
    respectively as required by the GLX and EGL specifications.
* Sun Mar 23 2014 bumblebee.obs@gmail.com
- Update to 334.21
  * Added support for the following GPUs:
    GeForce GTX 750 Ti
    GeForce GTX 750
    GeForce GTX 745
    GeForce GTX TITAN Black
    GeForce GT 710
    GeForce 825M
  * Fixed a regression in the NVIDIA kernel module which caused it to
    improperly dereference a userspace pointer. This potential security
    issue was initially reported to the public at:
    http://forums.grsecurity.net/viewtopic.php?f=3&t=3922
  * The regression did not affect NVIDIA GPU drivers before release 334.
  * Fixed a bug that could cause OpenGL programs to hang after calling fork(2).
  * Fixed a bug that could cause a multi-threaded OpenGL application to
    crash when one of its threads exits after the application has unloaded libGL.
  * Added support for GPUs with VDPAU Feature Set E. See the README for details.
  * On GPUs with VDPAU Feature Set E, VDPAU now supports more robust decode
    error handling at the cost of a minor performance impact. This can be
    disabled by setting the VDPAU_NVIDIA_DISABLE_ERROR_CONCEALMENT environment
    variable to 1.
  * Added support for application profile rule patterns which are logical
    operations of subpatterns. See the README for details.
  * Added support for a "findfile" application profile feature which allows
    the driver to apply profiles based on matching files in the same directory
    as the process executable. See the README for details.
  * Fixed a bug that caused nvidia-installer to log the automatically selected
    answers to some user prompts without logging the prompt text itself,
    when running in silent mode.
  * Improved performance of OpenGL applications when used in conjunction with
    the X driver's composition pipeline. The composition pipeline may be
    explicitly enabled by using the ForceCompositionPipeline or
    ForceFullCompositionPipeline MetaMode options, or implicitly enabled when
    certain features such as some XRandR transformations, rotation,
    Warp & Blend, PRIME, and NvFBC are used.
  * Fixed a bug that could cause nvidia-settings to crash or display
    incorrect information after switching virtual terminals while a color
    correction confirmation countdown was active.
  * Improved compatibility with recent Linux kernels.
* Sun Feb 23 2014 bumblebee.obs@gmail.com
- Update to 334.16
  * Fixed a bug that could cause nvidia-settings to compute incorrect gamma ramps
    when adjusting the color correction sliders.
  * Updated the nvidia-settings control panel to allow the selection of display
    devices using RandR and target ID names when making queries targeted towards
    specific display devices.
  * Fixed a bug that prevented some dropdown menus in the nvidia-settings control
    panel from working correctly on older versions of GTK+ (e.g. 2.10.x).
  * Updated the nvidia-settings control panel to provide help text for application
    profile keys and suggestions for valid key names when configuring application
    profiles.
  * Updated the nvidia-settings control panel to populate the dropdown menu of
    stereo modes with only those modes which are available.
  * Fixed a bug that could cause applications using the OpenGL extension
    ARB_query_buffer_object to crash under Xinerama.
  * Fixed a bug that caused high pixelclock HDMI modes (e.g. as used with
    4K resolutions) to be erroneously reported as dual-link in the
    nvidia-settings control panel.
  * Fixed a bug that could cause poor stereo synchronization in large multi-monitor
    setups using 3D Vision, due to failed hardware handshaking on some of the monitors.
  * Fixed a bug that prevented some DisplayPort 1.2 displays from being properly
    restored after a VT switch.
  * Renamed per GPU proc directories in /proc/driver/nvidia/gpus/ with GPU's bus
    location represented in "domain:bus:device.function" format.
  * Added 64-bit EGL and OpenGL ES libraries to 64-bit driver prackages.
  * Changed format of "Bus Location" field reported in the
    /proc/driver/nvidia/gpus/0..N/information files from "domain:bus.device.function"
    to "domain:bus:device.function" to match the lspci format.
  * Fixed a bug in the GLX_EXT_buffer_age extension where incorrect ages would be
    returned unless triple buffering was enabled.
  * Updated the NVIDIA X driver to load the NVIDIA kernel module using
    `nvidia-modprobe`, rather than the XFree86 DDX helper function
    xf86LoadKernelModule().
  * Changed the driver's default behavior to stop deleting RandR 1.2 outputs
    corresponding to unused DisplayPort 1.2 devices.  Deleting these outputs can
    confuse some applications.  Added a new option, DeleteUnusedDP12Displays, which
    can be used to turn this behavior back on.
    This option can be enabled by running
    sudo nvidia-xconfig --delete-unused-dp12-displays
  * Improved support for the __GL_SYNC_DISPLAY_DEVICE and
    VDPAU_NVIDIA_SYNC_DISPLAY_DEVICE environment variables in certain configurations.
    Both environment variables will now recognize all supported display device names.
    See "Appendix C. Display Device Names" and "Appendix G. VDPAU Support" in the
    README for more details.
  * Improved performance of the X driver when handling large numbers of
    surface allocations.
  * Fixed a bug that caused PBO downloads of cube map faces to retrieve
    incorrect data.
  * Fixed a bug in nvidia-installer that resulted in spurious error messages when
    opting out of installing the NVIDIA kernel module or source files for the
    kernel module.
  * Added experimental support for ARGB GLX visuals when Xinerama and Composite are
    enabled at the same time on X.Org xserver 1.15.
* Sun Feb 23 2014 bumblebee.obs@gmail.com
- Update to 331.49
  * Added support for the following GPUs:
    GeForce GT 710
    GeForce 825M
  * Fixed a regression that prevented nvidia-installer from cleaning up directories
    created as part of the driver installation.
  * Added a new X configuration option "InbandStereoSignaling" to enable/disable
    DisplayPort in-band stereo signaling. See "Appendix B. X Config Options" in the
    README for more information.
  * Fixed a bug that caused PBO downloads of cube map faces to retrieve
    incorrect data.
  * Fixed a bug in nvidia-installer that resulted in spurious error messages when
    opting out of installing the NVIDIA kernel module or source files for the
    kernel module.
  * Added experimental support for ARGB GLX visuals when Xinerama and Composite are
    enabled at the same time on X.Org xserver 1.15.
  * Fixed a bug which could sometimes corrupt a newly-created thread's signal mask in
    multi-threaded applications that load libGL.
  * Fixed a bug that prevented the NVIDIA implementation of the Xinerama extension
    protocol requests from being used when RandR was enabled.
* Tue Jan 14 2014 bumblebee.obs@gmail.com
- Update to 331.38
  * Fixed a bug that caused the X server to crash if video memory is exhausted
    and the GPU does not support rendering to system memory.
  * Updated nvidia-installer to make the --multiple-kernel-modules option imply
    the --no-unified-memory option: Unified memory is incompatible with multiple
    kernel modules.
  * Updated the behavior of the nvidia-settings PowerMizer Preferred Mode
    drop-down menu, to make the setting apply consistently across all GPUs
    in an SLI group.
  * Improved the robustness of the NVIDIA X driver in scenarios where
    GPU-accessible memory for allocating pixmaps was exhausted.
  * Added NV-CONTROL attributes to control the brightness of the illuminated
    logos on certain graphics boards.For example, to turn off the illumination
    of the "GEFORCE GTX" lettering on the GeForce GTX 780, use
    nvidia-settings --assign GPULogoBrightness=0
  * Fixed a bug that prevented screen transformations from being applied
    properly when starting X.
  * GLX protocol for the following OpenGL extensions from OpenGL 2.1 and
    OpenGL 3.0 have been promoted from unofficial to ARB approved official status:
    GL_ARB_pixel_buffer_object
    GL_NV_conditional_render
    GL_ARB_map_buffer_range
    GL_EXT_texture_integer
    GL_ARB_vertex_array_object
    GL_ARB_pixel_buffer_object was the last piece of protocol needed to have
    official support for indirect rendering with all OpenGL 2.1 commands.
  * GLX Protocol for the miscellaneous OpenGL 3.0 commands not associated with
    specific extensions has also been promoted from unofficial to ARB approved status.
    Deprecated display mask related configuration of display devices via NV-CONTROL
    and nvidia-settings.Display target specifications should be used instead - A display
    target is one of the display's valid names, with an optional GPU or X screen qualifier.
    Deprecated the following NV-CONTROL attributes:
    NV_CTRL_CONNECTED_DISPLAYS
    NV_CTRL_ENABLED_DISPLAYS
    NV_CTRL_ASSOCIATED_DISPLAYS
    NV_CTRL_NOTEBOOK_INTERNAL_LCD
    NV_CTRL_FRAMELOCK_MASTER
    NV_CTRL_FRAMELOCK_SLAVES
    NV_CTRL_FRAMELOCK_MASTERABLE
    NV_CTRL_FRAMELOCK_SLAVEABLE
    Also, although NV_CTRL_PROBE_DISPLAYS is still operational, the return value has
    been deprecated and should not be used.
  * Added deprecation warning messages in nvidia-settings when deprecated attributes
    are used.This also includes display mask usage.
* Mon Nov 11 2013 bumblebee.obs@gmail.com
- Update to 331.20
  * Added support for NVIDIA OpenGL-based Framebuffer Capture (NvFBCOpenGL).
    This library provides a high performance, low latency interface to capture
    and optionally encode the composited framebuffer of an X screen.
    NvFBC and NvIFR are private APIs that are only available to approved partners
    for use in remote graphics scenarios.  Please contact NVIDIA at
    GRIDteam@nvidia.com for more information.
  * Fixed a bug that prevented configuration files containing application profiles
    from being loaded when directories were present in the application profile
    configuration search path.
  * Deferred initialization of libselinux in the NVIDIA OpenGL driver, in order to
    avoid a problem where libselinux might not be ready when the NVIDIA
    libGL shared library is first loaded.
  * Fixed a bug that could lead to memory exhaustion in OpenGL applications
    running on 32-bit systems.
  * Added nvidia-uvm.ko, the NVIDIA Unified Memory kernel module, to the NVIDIA
    Linux driver package. This kernel module provides support for the new
    Unified Memory feature in an upcoming CUDA release.
  * Fixed a bug that caused the X server to fail to initialize when DisplayPort 1.2
    monitors were assigned to separate X screens on the same GPU.
  * Fixed a bug that could cause a deadlock when forking from OpenGL programs
    which use some malloc implementations, such as TCMalloc.
  * Fixed a bug that prevented Warp & Blend settings from being retained across
    display configuration changes.
  * Fixed a bug that prevented some settings changes made via the nvidia-settings
    command line interface from being reflected in the nvidia-settings
    graphical user interface.
  * Changed the clipping behavior of the NVIDIA X driver on Trapezoids and
    Triangles for some RENDER operations to match the behavior in newer
    versions of Pixman:
  * http://lists.freedesktop.org/archives/pixman/2013-April/002755.html
  * Fixed a bug in MetaMode tracking that could cause spurious error messages
    to be printed when attempting to add or delete Metamodes via NV-CONTROL.
  * Fixed a bug that caused the NVIDIA X driver to attempt to load the
    X11 "shadow" module unconditionally, even in situations where the driver
    had no need to use the module. This could result in the printing of
    spurious error messages, on X servers where the module was not present.
  * Fixed a bug that prevented display configuration changes made with
    xvidtune(1) from working correctly.
  * Fixed a bug that occasionally caused display corruption in GLX applications
    while changing the display configuration.
  * Fixed a bug that prevented glReadPixels from working correctly when reading
    from Pixel Buffer Objects over indirect rendering, when the image width is
    not a multiple of 4.
  * Added a new NV-CONTROL attribute, NV_CTRL_BACKLIGHT_BRIGHTNESS, for
    controlling backlight brightness.
  * Fixed a bug that prevented nvidia-settings from creating display device
    configuration pages for newly connected DisplayPort 1.2 Multi Stream
    Transport downstream devices.
  * Added GPU utilization reporting to the nvidia-settings control panel.
  * Fixed a bug in the nvidia-settings control panel that prevented users from
    configuring stereo, when stereo was not already configured.
  * Added support for reporting the tachometer-measured fan speed on capable
    graphics boards via nvidia-settings and the NV-CONTROL API. The preexisting
    mechanism for reporting fan speed reports the speed of the fan as
    programmed by the driver.
  * For example, `nvidia-settings --query=[fan:0]/GPUCurrentFanSpeedRPM`.
  * Fixed a regression that caused GPUs that do not support graphics to not
    appear in nvidia-settings.
  * Fixed a bug that caused DisplayPort 1.2 multi-stream devices to stop working
    if they were unplugged and plugged back in while they were active in the
    current MetaMode.
  * Added support for multiple NVIDIA kernel modules. This feature allows users
    to assign different GPUs in the system to different NVIDIA kernel modules,
    potentially reducing the software overhead of coordinating access to multiple GPUs.
  * Added support for the EGL API on 32-bit platforms.  Currently, the
    supported client APIs are OpenGL ES 1.1, 2.0 and 3.0, and the only
    supported window system backend is X11.
  * Add a new option, AllowEmptyInitialConfiguration, which allows the X server
    to start even if no connected display devices are detected at startup.
    This option can be enabled by running
    "sudo nvidia-xconfig --allow-empty-initial-configuration"
  * This option is useful in RandR 1.4 display offload configurations where
    no display devices are connected to the NVIDIA GPU when the X server is
    started, but might be connected later.
  * Updated nvidia-installer to provide a scrollable text area for
    displaying messages from the /usr/lib/nvidia/alternate-install-present and
    /usr/lib/nvidia/alternate-install-available distro hook files. This allows
    for longer messages to be provided in these files.
  * Updated nvidia-installer to avoid recursing into the per-kernel "build" and
    "source" directories when searching for conflicting kernel modules
    in /lib/modules.
  * Added a system memory cache to improve the performance of certain
    X rendering operations that use software rendering fallbacks.  The
    X configuration option "SoftwareRenderCacheSize" may be used to configure
    the size of the cache.
  * Removed the "DynamicTwinView" X configuration option: dynamic
    reconfiguration of displays is always possible, and can no longer
    be disabled.
  * Fixed a bug that caused nvidia-settings to display incorrect information
    in its display configuration page when all displays on
    an X screen were turned off.
  * Updated nvidia-installer to only install the libraries libvdpau and
    libvdpau_trace if an existing installation of libvdpau is not detected
    on the system. This behavior can be overridden with
    the --install-vdpau-wrapper and --no-install-vdpau-wrapper options.
  * Future NVIDIA Linux installer packages will no longer include copies of
    libvdpau or libvdpau_trace: VDPAU users are recommended to install these
    libraries via other means, e.g. from packages provided by their
    distributors, or by building them from the sources available
    at: http://people.freedesktop.org/~aplattner/vdpau/
* Wed Oct 23 2013 bumblebee.obs@gmail.com
- Update to 331.17
  * Fixed a bug that prevented configuration files containing application
    profiles from being loaded when directories were present in the
    application profile configuration search path.
  * Deferred initialization of libselinux in the NVIDIA OpenGL driver,
    in order to avoid a problem where libselinux might not be ready
    when the NVIDIA libGL shared library is first loaded.
  * Fixed a bug that could lead to memory exhaustion in OpenGL
    applications running on 32-bit systems.
  * Added nvidia-uvm.ko, the NVIDIA Unified Memory kernel module,
    to the NVIDIA Linux driver package. This kernel module provides
    support for the new Unified Memory feature in an upcoming CUDA release.
* Fri Oct  4 2013 bumblebee.obs@gmail.com
- Update to 331.13
  * Fixed a bug that caused the X server to fail to initialize when
    DisplayPort 1.2 monitors were assigned to separate X screens on
    the same GPU.
  * Fixed a bug that could cause a deadlock when forking from OpenGL programs
    which use some malloc implementations, such as TCMalloc.
  * Fixed a bug that prevented Warp & Blend settings from being retained
    across display configuration changes.
  * Fixed a bug that prevented some settings changes made via the
    nvidia-settings command line interface from being reflected in the
    nvidia-settings graphical user interface.
  * Changed the clipping behavior of the NVIDIA X driver on Trapezoids and
    Triangles for some RENDER operations to match the behavior in newer
    versions of Pixman:
    http://lists.freedesktop.org/archives/pixman/2013-April/002755.html
  * Fixed a bug in MetaMode tracking that could cause spurious error messages
    to be printed when attempting to add or delete Metamodes via NV-CONTROL.
  * Fixed a bug that caused the NVIDIA X driver to attempt to load the
    X11 "shadow" module unconditionally, even in situations where the driver
    had no need to use the module. This could result in the printing of
    spurious error messages, on X servers where the module was not present.
  * Fixed a bug that prevented display configuration changes made with
    xvidtune(1) from working correctly.
  * Fixed a bug that occasionally caused display corruption in GLX applications
    while changing the display configuration.
  * Fixed a bug that prevented glReadPixels from working correctly when
    reading from Pixel Buffer Objects over indirect rendering,
    when the image width is not a multiple of 4.
  * Added a new NV-CONTROL attribute, NV_CTRL_BACKLIGHT_BRIGHTNESS,
    for controlling backlight brightness.
  * Fixed a bug that prevented nvidia-settings from creating display device
    configuration pages for newly connected DisplayPort 1.2 Multi Stream
    Transport downstream devices.
  * Added GPU utilization reporting to the nvidia-settings control panel.
  * Fixed a bug in the nvidia-settings control panel that prevented users
    from configuring stereo, when stereo was not already configured.
  * Added support for reporting the tachometer-measured fan speed on capable
    graphics boards via nvidia-settings and the NV-CONTROL API. The preexisting
    mechanism for reporting fan speed reports the speed of the fan as
    programmed by the driver.
    For example, `nvidia-settings --query=[fan:0]/GPUCurrentFanSpeedRPM`.
  * Fixed a regression that caused GPUs that do not support graphics to not
    appear in nvidia-settings.
  * Fixed a bug that caused DisplayPort 1.2 multi-stream devices to stop
    working if they were unplugged and plugged back in while they were
    active in the current MetaMode.
  * Added support for multiple NVIDIA kernel modules. This feature allows
    users to assign different GPUs in the system to different NVIDIA kernel
    modules, potentially reducing the software overhead of coordinating
    access to multiple GPUs.
  * Added support for the EGL API on 32-bit platforms. Currently,
  the supported client APIs are OpenGL ES 1.1, 2.0 and 3.0, and the only
    supported window system backend is X11.
  * Add a new option, AllowEmptyInitialConfiguration, which allows the
    X server to start even if no connected display devices are detected
    at startup. This option can be enabled by running
    "sudo nvidia-xconfig --allow-empty-initial-configuration"
    This option is useful in RandR 1.4 display offload configurations where
    no display devices are connected to the NVIDIA GPU when the X server is
    started, but might be connected later.
    Updated nvidia-installer to provide a scrollable text area for displaying
    messages from the /usr/lib/nvidia/alternate-install-present and
    /usr/lib/nvidia/alternate-install-available distro hook files. This allows
    for longer messages to be provided in these files.
    Updated nvidia-installer to avoid recursing into the per-kernel "build" and
    "source" directories when searching for conflicting kernel modules
    in /lib/modules.
    Added a system memory cache to improve the performance of certain
    X rendering operations that use software rendering fallbacks. The X
    configuration option "SoftwareRenderCacheSize" may be used to configure
    the size of the cache.
    Removed the "DynamicTwinView" X configuration option: dynamic
    reconfiguration of displays is always possible, and can no longer be disabled.
    Fixed a bug that caused nvidia-settings to display incorrect information
    in its display configuration page when all displays on an X screen were
    turned off.
  * Updated nvidia-installer to only install the libraries libvdpau and
    libvdpau_trace if an existing installation of libvdpau is not detected
    on the system. This behavior can be overridden with
    the --install-vdpau-wrapper and --no-install-vdpau-wrapper options.
    Future NVIDIA Linux installer packages will no longer include copies of
    libvdpau or libvdpau_trace: VDPAU users are recommended to install
    these libraries via other means, e.g. from packages provided by their
    distributors, or by building them from the sources available at:
    http://people.freedesktop.org/~aplattner/vdpau/
* Sat Jul 20 2013 bumblebee.obs@gmail.com
- Update to 325.08
  * Fixed a bug that could cause display flickering after
    setting some scaling configurations.
  * Fixed a bug that prevented the status bar on the
    "PowerMizer" and "X Server XVideo Settings" pages in the
    nvidia-settings control panel from being updated when settings
    were changed by another NV-CONTROL client.
  * Fixed a bug that could cause some UI elements to be duplicated
    in the nvidia-settings control panel following a VT switch on
    X server configurations with multiple NVIDIA X screens.
  * Changed the default PCIe interrupt delivery method from
    virtual-wire to MSI. Note that if the NVIDIA Linux driver fails to
    initialize with an error indicating that it is not receiving interrupts,
    MSI can be disabled by setting the module parameter "NVreg_EnableMSI=0" when
    loading the NVIDIA kernel module.
  * Removed support for Linux 2.4 kernels. The NVIDIA Linux driver now
    requires Linux 2.6.9 or later.
  * Fixed a bug that prevented the creation of a mode via RandR with the same
    name as a previously created mode, even after the previous mode had been deleted.
  * Fixed a bug in nvidia-settings that caused GTK+ theme colors to be ignored
    for some UI elements.
  * Fixed a bug that caused nvidia-settings to write hostname-based color
    correction settings to the .nvidia-settings-rc configuration file,
    even when the "Include X Display Names in the Config File" option was unset.
    This could lead to a long delay when starting nvidia-settings, if a hostname
    saved to the configuration file failed to resolve.
  * Fixed a bug that exposed edge overlap controls on the SLI Mosaic page of
    nvidia-settings on edges where overlap was impossible.
  * Fixed a bug that caused some settings in the nvidia-settings control panel to
    be reset when reprobing displays.
  * Fixed a bug that could cause OpenGL applications that use
    Frame Buffer Objects (FBOs) to crash following a mode switch
    (e.g. changing the resolution of a display or transforming it).
  * Fixed a memory leak that could be triggered by unloading libGL before
    destroying all GLX contexts.
  * Fixed a bug that could cause color correction settings to be applied to
    the wrong display when multiple displays are unplugged and then plugged
    back in again.
  * Fixed a bug that could cause a spurious error message about a missing
    NV-GLX extension when performing indirect rendering from a GLX client with
    the NVIDIA client-side OpenGL libraries to a non-NVIDIA GLX server.
  * Fixed an OpenGL bug that prevented conditional rendering from the
    NV_conditional_render extension from correctly affecting CopyPixels.
  * Improved the rendering performance of complex gradients.
  * Added support for configuring SLI Mosaic and Base Mosaic in the
    "X Server Display Configuration" page of nvidia-settings.
  * Updated nvidia-installer to look for the following files:
    /usr/lib/nvidia/alternate-install-available
    /usr/lib/nvidia/alternate-install-present
  * These files may be provided by NVIDIA driver installers other than the
    official .run package maintained by NVIDIA, to alert nvidia-installer
    to the presence or availability of an alternative installation method.
    See the nvidia-installer(1) manual page for more information.
  * Fixed an X driver bug where the RandR CRTC panning area and tracking area
    were not getting clamped to the current X screen size when the RandR CRTC
    transitioned from disabled to enabled.
  * Fixed an X driver bug where successful RandR X_RRSetScreenConfig requests
    would update the server's RandR 'lastSetTime' too far, potentially causing
    subsequent RandR requests to be unnecessarily rejected.
  * Fixed an X driver bug that caused GPUs to become inaccessible via the
    NV-CONTROL X extension when no corresponding X screens could be initialized.
  * Generate a BadMatch error when applications attempt to create GLX pixmaps
    using glXCreatePixmap() or glXCreateGLXPixmapWithConfigSGIX() and the pixmap's
    depth doesn't match that of the specified GLXFBConfig.
  * Updated nvidia-settings to explicitly specify the direction of rotation for
    configuring per-display rotation configuration.
  * Honor a GPU UUID as the GPU qualifier for X configuration options that allow
    GPU qualifiers (e.g. "MetaModes").
  * Report GPU UUIDs in the X log when verbose logging is enabled in the X server.
  * Enabled conformant glBlitFrameBuffer() scissor test behavior by default.
    A driver-provided application profile enables the previous non-conformant
    behavior for applications that load libcogl, to work around a bug in older
    versions of libcogl.
  * Application profiles can be added to enable the non-conformant behavior
    for other applications that depend upon it. See the "Known Issues" section of
    the README for more details.
  * Fixed a bug that caused the X server to crash when querying the current mode
    of disabled displays.
* Sat Jul 20 2013 bumblebee.obs@gmail.com
- Update to 319.32
  * Added support for the following GPU:
    GeForce GTX 760
    GeForce 720M
  * Updated the nvidia-settings control panel to report more
    detailed locking information.
  * Fixed a bug that could cause the X server to crash after power-cycling
    displays connected behind a DisplayPort 1.2 Multi-Stream Transport hub.
  * Fixed a bug that could cause nvidia-settings to crash when switching
    VTs after changing some settings.
  * Updated the application profile syntax to allow for multiple patterns
    within a single rule. See the README for details.
  * Fixed a bug that caused OpenGL programs to crash when the
  __GL_DOOM3 environment variable was set.
  * Updated the NVIDIA driver to avoid calling fork(2) to execute the
    nvidia-modprobe utility when not needed.
  * Improved the error reporting of the nvidia-persistenced utility.
  * Fixed a bug that could cause Altair HyperView to hang when rendering
    animations with tensors.
  * Fixed a performance regression in MEDINA 8.2.
  * Fixed a bug that caused the OpenGL driver to hang sometimes when running
    the SpeedTree Modeler application.
  * Fixed a bug that could cause an OpenGL application to crash if it creates
    and destroys multiple threads.
  * Fixed a bug in nvidia-installer that could cause installation problems
    when the value of the CC environment variable contained spaces,
    e.g. CC="distcc gcc"
  * Fixed a bug that caused corrupted window content in some cases when
    moving GLX windows with antialiasing enabled.
  * Fixed a bug that caused DisplayPort devices that failed link training
    to be reported as connected rather than disconnected.
  * Fixed a regression that could cause a DisplayPort device that was connected
    to one connector to turn off when a DisplayPort device on a different
    connector was connected or disconnected.
  * On Kepler-based GPUs, improved the appearance of the tearing that occurs
    when using RandR 1.4's Source Output capability.While tearing is still
    expected, the tears should now appear as horizontal lines rather than
    more noticeable checkerboard or triangular shapes.
  * Added a "Prefer Consistent Performance" PowerMizer Mode to the
    nvidia-settings control panel, available on Quadro boards that support
    this feature.
* Fri May 31 2013 bumblebee.obs@gmail.com
- Update to 319.23
  * Added support for the following GPUs:
    GeForce GTX 780
  * Fixed a regression that could cause X to crash when querying GPU information
  through NV-CONTROL on multi-GPU systems where some GPUs failed to be
    initialized for X.
  * Fixed a bug that could cause X to crash when using Vertex Buffer Objects (VBOs)
  with indirect rendering.
  * Fixed a bug that prevented some drop-down menus in nvidia-settings from
  working correctly when using older versions of GTK+.
  * Fixed RandR panning reporting when the current MetaMode is smaller than
  the X screen.
  * Fixed a regression that caused nvidia-installer to attempt post-processing of
  non-installed files.
  * Added the "ForceCompositionPipeline" and "ForceFullCompositionPipeline" MetaMode
  options. See the README for details.
  * Added support for HDMI 4K resolutions. Using a 4K resolution with an HDMI display
  requires a Kepler or later GPU.
  * Added support in VDPAU for 4k resolution MPEG-1/2 and H.264 video decoding,
  up to 4032x4048 for MPEG-1/2 and 4032x4080 for H.264, and up to 65536 macroblocks for both.
* Fri May 10 2013 bumblebee.obs@gmail.com
- Update to 319.17
  * Added support for the following GPU:
    GeForce GTX 650 Ti BOOST
    GeForce GT 720M
    GeForce GT 735M
    GeForce GT 740M
    GeForce GT 745M
    GeForce GT 750M
  * Fixed a regression that caused multiple BUG messages to be printed in
    the kernel log on SMP systems.
  * Fixed a bug that could cause the X server to crash when repeatedly
    enabling and disabling displays.
  * Updated nvidia-settings to preserve the relative positioning of displays when
    changing from a layout where multiple displays are on the same X screen to
    one where the same displays span multiple X screens.
  * Fixed nvidia-settings to dlopen(3) "libvdpau.so.1", rather than "libvdpau.so".
  * Added nvidia-persistenced, a daemon utility, to the driver package.
    nvidia-persistenced can be installed to run on system startup or manually
    run to allow the NVIDIA kernel module to keep persistent driver state allocated
    when no other user-space NVIDIA driver components are running. This can improve
    startup time for other user-space NVIDIA driver components.
  * Fixed CVE-2013-0131: NVIDIA UNIX GPU Driver ARGB Cursor Buffer Overflow in
    "NoScanout" Mode. This buffer overflow, which occurred when an X client
    installed a large ARGB cursor on an X server running in NoScanout mode,
    could cause a denial of service (e.g., an X server segmentation fault),
    or could be exploited to achieve arbitrary code execution.
  * For more details, see: http://nvidia.custhelp.com/app/answers/detail/a_id/3290
  * Added initial support for restoration of efifb consoles on UEFI systems where
    the primary display is driven over VGA or TMDS (e.g. DVI, HDMI, or LVDS).
  * Added support for the xorg.conf Monitor section options "Ignore", "Enable",
    "Primary", and "Rotate".For example, to rotate a monitor identified by
    a specific EDID hash, one could add the following to /etc/X11/xorg.conf or
    a file in /etc/X11/xorg.conf.d:
    Section "Monitor"
    Identifier "DPY-EDID-ee6cecc0-fa46-0c33-94e0-274313f9e7eb"
    Option "Rotate" "left"
    EndSection
    See the README and the xorg.conf(5) man page for more information.
  * Added an Underscan feature in the nvidia-settings X Server Display
    Configuration page which allows the configuration of an underscan border
    around the ViewPortOut.This feature was formerly known as Overscan Compensation.
  * Added support for application profiles to the NVIDIA client-side GLX
    implementation. See the "Application Profiles" chapter of
    the README for more information.
  * Added support to nvidia-installer for crytographically signing the NVIDIA
    kernel module. See the "Installing the NVIDIA Driver" chapter of
    the README for more information.
  * Added the "PanningTrackingArea" and "PanningBorder" MetaMode attributes.
  * Added support for RandR 1.3 panning.
  * Improved performance when the Accel option is disabled.
  * Added initial support for RandR 1.4 Provider objects with the Source Output
    capability, which can be used to render the desktop on an NVIDIA GPU and
    display it on an output connected to a provider with the Sink Output
    capability, such as an Intel integrated graphics device or a
    DisplayLink USB-to-VGA adapter.See the README for details.
  * Added nvidia-modprobe, a setuid root utility, to the driver package.
    nvidia-modprobe can be used by user-space NVIDIA driver components to
    make sure the NVIDIA kernel module is loaded and that the NVIDIA character
    device files are present.When possible, it is recommended to use Linux
    distribution native mechanisms for managing kernel module loading and
    device file creation. This utility is provided as a fallback to work
    out-of-the-box in a distribution-independent way.
  * Updated the nvidia-settings command line interface to accept display
    device names, as well as optional target qualifiers, e.g.
    nvidia-settings -q [DVI-I-0]/RefreshRate
    nvidia-settings -q [GPU-1.DVI_I-1]/RefreshRate
  * Updated the nvidia-settings command line interface to no longer assume
    the "X screen 0" target, when no target is specified in query and assign
    operations.Instead, all valid targets of the attribute are processed.
  * Fixed a memory leak that occurred when destroying a GLX window but
    not its associated X window.
  * Fixed a bug that could cause nvidia-installer to fail to delete directories
    created as part of a previous installation.
  * Updated nvidia-installer to report failures to remove installed files or
    restore backed up files with a single warning message, instead of a separate
    message for each individual failure.
  * Improved the performance of modesets in cases where the mode timings remained
    the same, but other parameters of the mode configuration, such as the
    ViewPort or panning domain, changed.
  * Fixed an issue with RENDER convolution filters.The driver will no longer
    normalize filter kernels before accelerating them.
  * Improved debuggability of the NVIDIA OpenGL libraries by including proper
    stack unwinding information on all supported architectures.
  * Updated the dkms.conf file and the makefile for the NVIDIA Linux kernel
    module to allow DKMS installations on systems with separate source and
    output directories.
  * Fixed a bug that caused RENDER Pictures to be sampled incorrectly when
    using nearest filtering in some cases.
  * Added support for the RandR "Border" and "BorderDimensions" Output
    properties, which can be used to configure the ViewPortOut of an RandR output.
    This is functionally equivalent to the "ViewPortOut" MetaMode token.
  * Fixed a bug where RRGetCrtcInfo could report incorrect size information
    when an RandR output has a custom ViewPortIn.
  * Further improve performance of some versions of HyperMesh with Quadro GPUs.
  * Added a VDPAU page to the nvidia-settings control panel, to display
    information about the decoding capabilities of VDPAU-capable GPUs.
  * Added support for dynamic mode management through RandR, e.g. via
    the --newmode, --rmmode, and --delmode options in xrandr(1).
  * Increased the number of pages that are shareable across multiple processes
    in the x86 build of libnvidia-glcore.so, by reducing its R_386_PC32
    relocation count.
  * Fixed a bug that caused XVideo applications to receive BadAlloc errors
    after VT switches and mode switches that occurred while a composite
    manager was running.
  * Removed the X driver's support for "CursorShadow".
  * Updated nvidia-installer to attempt unprelinking files whose checksums
    do not match the checksums recorded at installation time.
  * Switched .run package compression from gzip to xz.This provides
    a higher level of compression.
* Wed Apr 10 2013 bumblebee.obs@gmail.com
- Update to 319.12
  * Added support for the following GPU:
    GeForce GTX 650 Ti BOOST
  * Fixed CVE-2013-0131: NVIDIA UNIX GPU Driver ARGB Cursor Buffer Overflow in
    "NoScanout" Mode. This buffer overflow, which occurred when an X client
    installed a large ARGB cursor on an X server running in NoScanout mode,
    could cause a denial of service (e.g., an X server segmentation fault),
    or could be exploited to achieve arbitrary code execution.
    For more details, see: http://nvidia.custhelp.com/app/answers/detail/a_id/3290
  * Added initial support for restoration of efifb consoles on UEFI systems where
    the primary display is driven over VGA or TMDS (e.g. DVI, HDMI, or LVDS).
  * Added support for the xorg.conf Monitor section options "Ignore", "Enable",
    "Primary", and "Rotate". For example, to rotate a monitor identified by a specific
    EDID hash, one could add the following to /etc/X11/xorg.conf or a file
    in /etc/X11/xorg.conf.d:
    Section "Monitor"
    Identifier "DPY-EDID-ee6cecc0-fa46-0c33-94e0-274313f9e7eb"
    Option "Rotate" "left"
    EndSection
    See the README and the xorg.conf(5) man page for more information.
  * Added an Underscan feature in the nvidia-settings X Server Display Configuration page
    which allows the configuration of an underscan border around the ViewPortOut.
    This feature was formerly known as Overscan Compensation.
  * Added support for application profiles to the NVIDIA client-side GLX implementation.
    See the "Application Profiles" chapter of the README for more information.
  * Added support to nvidia-installer for crytographically signing the NVIDIA kernel module.
    See the "Installing the NVIDIA Driver" chapter of the README for more information.
  * Added the "PanningTrackingArea" and "PanningBorder" MetaMode attributes.
  * Added support for RandR 1.3 panning.
  * Improved performance when the Accel option is disabled.
  * Added initial support for RandR 1.4 Provider objects with the Source Output capability,
    which can be used to render the desktop on an NVIDIA GPU and display it on an output
    connected to a provider with the Sink Output capability, such as an Intel integrated
    graphics device or a DisplayLink USB-to-VGA adapter.See the README for details.
  * Added nvidia-modprobe, a setuid root utility, to the driver package. nvidia-modprobe can be
    used by user-space NVIDIA driver components to make sure the NVIDIA kernel module is
    loaded and that the NVIDIA character device files are present.When possible, it is
    recommended to use Linux distribution native mechanisms for managing kernel module loading and
    device file creation. This utility is provided as a fallback to work out-of-the-box in
    a distribution-independent way.
  * Updated the nvidia-settings command line interface to accept display device names,
  as well as optional target qualifiers, e.g.
    nvidia-settings -q [DVI-I-0]/RefreshRate
    nvidia-settings -q [GPU-1.DVI_I-1]/RefreshRate
  * Updated the nvidia-settings command line interface to no longer assume the "X screen 0" target,
    when no target is specified in query and assign operations.Instead, all valid targets of
    the attribute are processed.
  * Fixed a memory leak that occurred when destroying a GLX window but not its associated X window.
  * Fixed a bug that could cause nvidia-installer to fail to delete directories created as
    part of a previous installation.
  * Updated nvidia-installer to report failures to remove installed files or restore backed up files
    with a single warning message, instead of a separate message for each individual failure.
  * Improved the performance of modesets in cases where the mode timings remained the same,
    but other parameters of the modeconfiguration, such as the ViewPort or panning domain, changed.
  * Fixed an issue with RENDER convolution filters.The driver will no longer normalize filter
    kernels before accelerating them.
  * Improved debuggability of the NVIDIA OpenGL libraries by including proper stack unwinding
    information on all supported architectures.
  * Updated the dkms.conf file and the makefile for the NVIDIA Linux kernel module to allow DKMS
    installations on systems with separate source and output directories.
  * Fixed a bug that caused RENDER Pictures to be sampled incorrectly when using nearest filtering
    in some cases.
  * Added support for the RandR "Border" and "BorderDimensions" Output properties,
    which can be used to configure the ViewPortOut of an RandR output.This is functionally
    equivalent to the "ViewPortOut" MetaMode token.
  * Fixed a bug where RRGetCrtcInfo could report incorrect size information when an RandR output
    has a custom ViewPortIn.
  * Further improve performance of some versions of HyperMesh with Quadro GPUs.
  * Added a VDPAU page to the nvidia-settings control panel, to display information about the
    decoding capabilities of VDPAU-capable GPUs.
  * Added support for dynamic mode management through RandR, e.g. via the --newmode, --rmmode,
    and --delmode options in xrandr(1).
  * Increased the number of pages that are shareable across multiple processes in the x86 build of
    libnvidia-glcore.so, by reducing its R_386_PC32 relocation count.
  * Fixed a bug that caused XVideo applications to receive BadAlloc errors after VT switches and
    mode switches that occurred while a composite manager was running.
  * Removed the X driver's support for "CursorShadow".
  * Updated nvidia-installer to attempt unprelinking files whose checksums do not match the
    checksums recorded at installation time.
  * Switched .run package compression from gzip to xz.This provides a higher level of compression.
* Wed Apr 10 2013 bumblebee.obs@gmail.com
- Update to 310.44
  * Fixed CVE-2013-0131: NVIDIA UNIX GPU Driver ARGB Cursor Buffer Overflow in
    "NoScanout" Mode. This buffer overflow, which occurred when an X client
    installed a large ARGB cursor on an X server running in NoScanout mode,
    could cause a denial of service (e.g., an X server segmentation fault),
    or could be exploited to achieve arbitrary code execution.
    For more details, see: http://nvidia.custhelp.com/app/answers/detail/a_id/3290
* Mon Mar 11 2013 bumblebee.obs@gmail.com
- Update to 310.40
  * Added support for the following GPUs:
    Quadro K4000
    Quadro K2000
    Quadro K2000D
    Quadro K600
    GeForce G205M
    GeForce GT 240M LE
    GeForce 405M
    GeForce 610
    GeForce 615
    GeForce 620M
    GeForce GT 625M
    GeForce GT 625 (OEM)
    GeForce GT 635
    GeForce 705M
    GeForce 710M
    GeForce GT 710M
    GeForce GT 720A
    GeForce GT 730M
    Tesla X2070
    Tesla S2050
    Tesla K20s
  * Reduced the amount of time needed to establish framelock in some stereo
    configurations with many monitors.
  * Fixed a bug where glXSwapIntervalEXT failed to set a swap interval value of zero
    in certain situations.
* Mon Jan 21 2013 bumblebee.obs@gmail.com
- Update to 310.32
  * Added support for the following GPUs:
    GeForce GTX 680MX
    Tesla K20Xm
  * Fixed a bug when enabling framelock between displays connected to the same GPU
    as other displays with different refresh rates, which caused the latter to be
    incorrectly assigned to the framelock group.
  * Updated the reporting of HDMI 3D framerates and pixel clocks to be more consistent
    with how they are reported by HDMI 3D displays.
  * Fixed a bug that sometimes prevented rotation controls in the nvidia-settings
    control panel from working after changing resolutions.
  * Fixed a bug that could cause applications using GL_NV_vdpau_interop to crash
    during modeswitches.
  * Fixed a regression that could cause OpenGL applications to crash while compiling
    shaders.
  * Added a kernel module parameter, "NVreg_EnablePCIeGen3", which can be used to
    enable PCIe gen 3 when possible. Note that on many systems where the NVIDIA driver
    does not allow PCIe gen 3 by default, stability problems can be expected when this
    option is enabled: users should do so at their own risk.
  * Fixed a VDPAU bug that could cause the X server to hang when decoding some corrupted
    video streams.
  * Renamed VGX products to GRID products in the "Supported NVIDIA GPU Products" list.
  * Added support for X.org xserver ABI 14 (xorg-server 1.14).
  * Fixed a bug in nvidia-settings that could cause the wrong resolution to be set in
    basic mode for setups based on one display per X screen.
  * Fixed libnvidia-encode.so library dependency by linking it with libnvcuvid.so.1 instead
    of libnvcuvid.so while creating it.
  * Improved performance of OpenGL framebuffer object binds with Xinerama enabled
    by 2000-3000%% when the application's windows do not span screen boundaries.
  * Fix performance issues when using some versions of HyperMesh with Quadro GPUs.
* Sat Dec 22 2012 bumblebee-project@hotmail.com
- Update to 313.09
  * Updated the NVIDIA X driver to reprobe displays when VT-switching to X, to allow
    reporting of hotplug events when displays are connected or disconnected while
    VT-switched away from X.
  * Added unofficial GLX protocol support (i.e for GLX indirect rendering) for the following
    extension and core commands.
    ARB_vertex_array_object
    OpenGL 3.0 commands ClearBufferfi, ClearBufferfv, ClearBufferiv, ClearBufferuiv and
    GetStringi.
  * Fixed a bug that caused the cursor shadow to be clipped to 32x32 pixels, even on
    Kepler GPUs that support a 256x256 cursor image.
  * Fixed a bug that prevented some cursor image updates from taking effect on displays with
    rotation or other transformations applied.
  * Fixed cursor alpha blending artifacts on displays with rotation or other
    transformations applied.
  * Added support for the GLX_EXT_buffer_age extension.
  * Improved the performance of glDrawPixels() by up to 450%% when the pixel data is of
    type GL_BYTE.
  * Fixed libnvidia-encode.so library dependency by linking it with libnvcuvid.so.1 instead of
    libnvcuvid.so while creating it.
  * Improved performance of OpenGL framebuffer object binds with Xinerama enabled by
  2000-3000%% when the application's windows do not span screen boundaries.
  * Fix performance issues when using some versions of HyperMesh with Quadro GPUs.
* Thu Nov 29 2012 bumblebee-project@hotmail.com
- Update to 310.19
  * Added support for OpenGL 4.3.
  * Added a new X configuration option, "UseHotplugEvents", to allow the suppression of
    RandR events when adding or removing non-DisplayPort displays. See the "X Config Options"
    appendix of the README for details.
  * Added support for configuring stereo in nvidia-settings when stereo is enabled in
    the X configuration file.
  * Added support for configuring the ViewPortIn and ViewPortOut for display devices in
    nvidia-settings.
  * Fixed metamode bookkeeping when modifying the display configuration in
    the "X Server Display Configuration" page of nvidia-settings.
  * Added support for configuring rotation and reflection per display device in
    nvidia-settings.
  * Implemented workarounds for two Adobe Flash bugs by applying libvdpau
    commit ca9e637c61e80145f0625a590c91429db67d0a40 to the version of libvdpau shipped with
    the NVIDIA driver.
  * Fixed an issue which affected the performance of moving windows of VDPAU applications when
    run in some composite managers.
  * Added unofficial GLX protocol support (i.e., for GLX indirect rendering) for
    the GL_ARB_pixel_buffer_object OpenGL extension.
  * Added support for HDMI 3D Stereo with Quadro Kepler and later GPUs. See the documentation for
    the "Stereo" X configuration option in the README for details.
  * Added experimental support for OpenGL threaded optimizations, available through
    the __GL_THREADED_OPTIMIZATIONS environment variable. For more information, please refer to
    the "Threaded Optimizations" section in chapter "Specifying OpenGL Environment Variable Settings"
    of the README.
  * Improved performance and responsiveness of windowed OpenGL applications running inside
    a Unity session.
* Tue Oct 16 2012 bumblebee-project@hotmail.com
- Update to 310.14
  * Implemented workarounds for two Adobe Flash bugs by applying libvdpau
    commit ca9e637c61e80145f0625a590c91429db67d0a40 to the version of libvdpau shipped
    with the NVIDIA driver.
  * Fixed an issue which affected the performance of moving windows of VDPAU applications
    when run in some composite managers.
  * Added unofficial GLX protocol support (i.e., for GLX indirect rendering) for
    the GL_ARB_pixel_buffer_object OpenGL extension.
  * Added support for HDMI 3D Stereo with Quadro Kepler and later GPUs. See the documentation
    for the "Stereo" X configuration option in the README for details.
  * Added experimental support for OpenGL threaded optimizations, available through
    the __GL_THREADED_OPTIMIZATIONS environment variable. For more information, please refer to
    the "Threaded Optimizations" section in chapter "Specifying OpenGL Environment Variable
    Settings" of the README.
  * Improved performance and responsiveness of windowed OpenGL applications running
    inside a Unity session.
  * Added support for OpenGL 4.3.
  * Added support for the "Backlight" RandR output property for configuring the brightness of
    some notebook internal panels.
  * Fixed a bug that prevented the Ubuntu Unity launcher panel from unhiding:
    https://bugs.launchpad.net/unity/+bug/1057000
  * Fixed a bug that caused nvidia-installer to sometimes attempt to write a log file in
    a nonexistent directory.
  * Fixed a bug that caused incorrect input transformation after resizing an NVIDIA X screen with
    xserver ABI 12 (xorg-server 1.12) or newer.
  * Fixed a bug that caused GLX to leak memory when Xinerama is enabled.
* Mon Sep 24 2012 bumblebee-project@hotmail.com
- Update to 304.51
  * Added support for the new Quadro Sync board for Quadro Kepler GPUs. See the
    "Configuring Frame Lock and Genlock" chapter in the README for details.
  * Fixed an X server crash on X.Org xserver 1.13 when it is compiled without support for DRI2.
  * Fixed a regression that broke color controls on older X servers.
  * Fixed a bug that sometimes caused the display layout area of the nvidia-settings
    control panel to be laid out incorrectly.
  * Fixed a bug that prevented panning from working correctly after a modeswitch on some
    X servers with support for cursor constraining.
  * Gamma ramp and colormap adjustments now apply correctly when screen transformations such as
    rotation and keystone correction are in use.
  * Fixed RandR per-CRTC gamma persistence across modeswitches and VT-switches.
  * Fixed a bug that caused the X server to sometimes hang in response to input events.
  * Fixed a reduction in rendering performance for core X11 rendering on certain GPUs that
    occurred in the 290.series of releases.
  * Fixed a bug that prevented PowerMizer from working correctly on some boards with GDDR5 memory,
    such as some GeForce GT 240 SKUs.
  * Fixed a bug that caused OpenGL applications to not animate properly when a rotation or
    a transformation was applied on some older X server versions.
  * Enabled FXAA with Unified Back Buffers.
  * Fixed a bug that prevented the "Reset Hardware Defaults" button in the Display Settings page of
    nvidia-settings from being activated.
* Tue Aug 28 2012 bumblebee-project@hotmail.com
- Update to 304.43
  * Added support for the following GPUs:
    GeForce GTX 660 Ti
    Quadro K5000
    Quadro K5000M
    Quadro K4000M
    Quadro K3000M
    NVS 510
  * Fixed a bug that caused pre-release versions of X.Org xserver 1.13 to crash when certain
    GLX operations were performed, such as when starting Firefox.
  * Fixed a bug that caused VDPAU to hang when expanding the YouTube Flash Player.
  * Fixed a bug that caused gnome-settings-daemon to revert display configuration changes
    made by nvidia-settings.
  * Updated nvidia-settings to use RandR per-CRTC gamma control, when available. When
    controlling an X server with support for RandR 1.2, nvidia-settings will display the color
    correction widget as a tab within each display device page, instead of a per-X screen color
    correction page.
  * Fixed a bug that prevented the display palette from being updated immediately after
    an application called XStoreColors.
  * Added the ability to select and move X screens in the "X Server Display Configuration" page of
    nvidia-settings via Ctrl-(Left)Click + Drag.
* Tue Aug 14 2012 bumblebee-project@hotmail.com
- Update to 304.37
  * Added support for the following GPUs:
    GeForce GTX 680M
    Quadro K1000M
    Quadro K2000M
    Tesla K10
  * Removed the ability to enable SLI on GPUs with ECC enabled.
  * Fixed several bugs that prevented some RandR transform geometries from being applied.
  * Fixed a bug that caused frequent hangs or crashes on some systems.
  * Fixed a bug that would cause corruption and performance issues in certain OpenGL applications
    such as Amnesia: The Dark Descent on GeForce 6 and 7 GPUs.
  * Fixed a bug that caused applications that use DirectColor visuals, such as
    Enemy Territory: Quake Wars and Braid, to appear in shades of blue instead of
    the correct colors.
  * Modified handling of RRSetScreenSize requests to ignore requests that do not actually resize
    the screen.This reduces screen flicker in certain cases when using GNOME.
  * Added a new option, "--disable-nouveau" to nvidia-installer. This option changes the action
    that is chosen by default when Nouveauis detected by nvidia-installer. If
    the "--disable-nouveau" optionis set, then the default will be to attempt to disable Nouveau
    when it is detected; otherwise, no attempt will be made unless requested.
  * Added support for xserver ABI 13 (xorg-server 1.13).
  * Added support for RandR per-CRTC gamma manipulation through the RandR 1.2 RRGetCrtcGammaSize,
    RRGetCrtcGamma, and RRSetCrtcGamma requests.
  * Fixed a bug that caused RRSetOutputPrimary requests to incorrectly generate BadValue errors
    when setting the primary output to None.This caused gnome-settings-daemon to crash after
    changing the screen configuration in response to a display hotplug or the display change
    hot-key being pressed.
  * Fixed a problem where RENDER Glyphs operations would exhibit severe performance issues in
    certain cases, such as when used with gradients by Cairo and Chromium.
  * Fixed a bug that caused X to hang when resuming certain DisplayPort display devices (such as
    Apple brand mini-DisplayPort to dual-link DVI adapters) from power-saving mode.
  * Fixed a bug that caused an X screen to be extended to Quadro SDI Output devices by default.
    An X screen will still use an SDI Output device if it is the only display device available.
    To use a SDI Output device on an X screen with other display devices available, include
    the SDI Output device with either the "UseDisplayDevice" or "MetaMode" X configuration options.
  * Updated X11 modeline validation such that modes not defined in a display device's EDID are
    discarded if the EDID 1.3 "GTF Supported" flag is unset or if
    the EDID 1.4 "Continuous Frequency" flag is unset. The new "AllowNonEdidModes" token for
    the ModeValidationX configuration option can be used to disable this new check.
  * Fixed a bug, introduced in the 295.xx release series, with EDID detection on some laptop
    internal panels. This bug caused the laptop internal panel to show six small copies of
    the desktop.
  * Added support for FXAA, Fast Approximate Anti-Aliasing. Using regular anti-aliasing modes or
    Unified Back Buffers with FXAA is not currently supported.
  * Enhanced the functionality of the IncludeImplicitMetaModes X configuration option:
    Implicit MetaModes will be added for the primary display device, even if multiple display
    devices are in use when X is initialized.
    Implicit MetaModes will be added for common resolutions, even
    if there isn't a mode with that resolution in the mode pool of
    the display device.
    Extended the syntax of the IncludeImplicitMetaModes X
    configuration option, e.g., to control which display device is
    used for creation of implicit MetaModes.
    See the description of the IncludeImplicitMetaModes X configuration
    option in the README for details.
  * Modified the handling of the RandR 1.0/1.1 requests RRGetScreenInfo and RRSetScreenConfig
    (e.g., `xrandr -q --q1` and `xrandr --size ...` and `xrandr --orientation ...`) such that
    they operate on MetaModes. This was the behavior in NVIDIA X driver versions 295.xx and
    earlier, but 302.xx releases altered the handling of these RandR 1.0/1.1 requests to
    operate on a single RandR output's modes.
  * With the above changes to IncludeImplicitMetaModes and RandR 1.0/1.1 handling, fullscreen
    applications (e.g., SDL-based applications, Wine), should have more resolutions available
    to them, and should interact better with multiple monitor configurations.
  * Fixed a bug that could cause G8x, G9x, and GT2xx GPUs to display a black screen or corruption
    after waking up from suspend.
  * Fixed several bugs that could cause some OpenGL programs to hang when calling fork(3).
  * Fixed an nvidia-settings bug that caused the results of ProbeDisplays queries made with
    the --display-device-string option to be formatted incorrectly.
  * Improved the responsiveness of updates to the nvidia-settings control panel when displays
    are hotplugged.
  * Fixed a bug that caused display corruption when setting some transforms, especially when
    panning a transformed display.
  * Fixed a bug that caused extra RandR events to be generated the first time a display is
    hotplugged.
  * Fixed a bug that caused X11 modelines with '@' in their names to be rejected.
  * Added support for DisplayPort 1.2 branch devices, which allow multiple displays to be
    connected to a single DisplayPort connector on a graphics board.
  * Fixed a bug that caused most OpenGL texture uploads to be slow when the context was
    bound rendering to an RGB overlay drawable.
  * Fixed a bug that caused audio over HDMI to not work after restarting the X server on
    some MCP7x (IGP) GPUs.
  * Updated the X configuration option "UseDisplayDevice" to honor the value "none" on any GPU.
  * Added support for DKMS in nvidia-installer. Installing the kernel module through DKMS
    allows the module to be rebuilt automatically when changing to a different Linux kernel.
    See the README and the nvidia-installer help text for the "--dkms" option.
  * Added RandR output properties _ConnectorLocation, ConnectorNumber, ConnectorType, EDID,
  _GUID, and SignalFormat. See the README for details on these properties.
  * Extended support for Base Mosaic to all G80+ SLI configurations with up to three displays.
  * Fixed a bug that caused some monitors to fail to wake from DPMS suspend mode when
    multiple DisplayPort monitors were attached to one GPU.
  * Removed controls for XVideo attributes from the "X Server XVideo Settings" page of
    the nvidia-settings control panel. XVideo attributes can be configured in XVideo player
    applications, or through utilities such as xvattr.
  * Fixed a bug that caused all ports on an XVideo adaptor to share color correction settings.
  * Removed support for the following X configuration options:
    SecondMonitorHorizSync
    SecondMonitorVertRefresh
    Similar control is available through the NVIDIA HorizSync and
    VertRefresh X configuration options. Please see the NVIDIA driver
    README for details.
  * Fixed a bug that prevented NVIDIA 3D Vision Pro from working properly when switching
    between X servers on different VTs.
  * Added support for desktop panning when rotation, reflection, or transformation is applied
    to a display device (either through RandR or through the MetaMode syntax); panning would
    previously be ignored in that case.
  * Implemented hotfix for a privilege escalation vulnerability reported on August 1, 2012.
    For more details, see: http://nvidia.custhelp.com/app/answers/detail/a_id/3140
* Tue Aug  7 2012 bumblebee-project@hotmail.com
- Update to 304.32
  * Implemented hotfix for a privilege escalation vulnerability reported on August 1, 2012.
    For more details, see: http://nvidia.custhelp.com/app/answers/detail/a_id/3140
  * Fixed a bug that caused applications that use Direct Color visuals, such as
    Enemy Territory: Quake Wars and Braid, to appear in shades of blue instead of
    the correct colors.
  * Modified handling of RRSetScreenSize requests to ignore requests that do not actually resize
    the screen. This reduces screen flicker in certain cases when using GNOME.
  * Added a new option, "--disable-nouveau" to nvidia-installer. This option changes the action
    that is chosen by default when Nouveau is detected by nvidia-installer. If
    the "--disable-nouveau" optionis set, then the default will be to attempt to disable Nouveau
    when it is detected; otherwise, no attempt will be made unless requested.
* Thu Aug  2 2012 bumblebee-project@hotmail.com
- Update to 304.30
  * Added support for the following GPU:
    Tesla K10
  * Added support for RandR per-CRTC gamma manipulation through the
    RandR 1.2 RRGetCrtcGammaSize, RRGetCrtcGamma, and RRSetCrtcGamma requests.
  * Fixed a bug that caused RRSetOutputPrimary requests to incorrectly generate BadValue
    errors when setting the primary output to None. This caused gnome-settings-daemon to
    crash after changing the screen configuration in response to a display hotplug or the
    display change hot-key being pressed.
  * Fixed a problem where RENDER Glyphs operations would exhibit severe performance issues
    in certain cases, such as when used with gradients by Cairo and Chromium.
  * Fixed a bug that caused X to hang when resuming certain DisplayPort display devices
    (such as Apple brand mini-DisplayPort to dual-link DVI adapters) from power-saving mode.
  * Fixed a bug that caused an X screen to be extended to Quadro SDI Output devices by default.
    An X screen will still use an SDI Output device if it is the only display device available.
    To use a SDI Output device on an X screen with other display devices available, include the
    SDI Output device with either the "UseDisplayDevice" or "MetaMode" X configuration options.
  * Updated X11 modeline validation such that modes not defined in a display device's EDID are
    discarded if the EDID 1.3 "GTF Supported" flag is unset or if the EDID 1.4 "Continuous Frequency"
    flag is unset. The new "AllowNonEdidModes" token for the ModeValidation X configuration option
    can be used to disable this new check.
  * Fixed a bug, introduced in the 295.xx release series, with EDID detection on some laptop
    internal panels. This bug caused the laptop internal panel to show six small copies of
    the desktop.
  * Added support for FXAA, Fast Approximate Anti-Aliasing.
* Thu Aug  2 2012 bumblebee-project@hotmail.com
- Update to 304.22
  * Added support for the following GPUs:
    GeForce GTX 680M
    Quadro K1000M
    Quadro K2000M
  * Enhanced the functionality of the IncludeImplicitMetaModes X configuration option:
    Implicit MetaModes will be added for the primary display device, even if multiple
    display devices are in use when X is initialized.
    Implicit MetaModes will be added for common resolutions, even if there isn't a mode
    with that resolution in the mode pool of the display device.
    Extended the syntax of the IncludeImplicitMetaModes X configuration option,
    e.g., to control which display device is used for creation of implicit MetaModes.
    See the description of the IncludeImplicitMetaModes X configuration option in the README
    for details.
  * Modified the handling of the RandR 1.0/1.1 requests RRGetScreenInfo and RRSetScreenConfig
    (e.g., `xrandr -q --q1` and `xrandr --size ...` and `xrandr --orientation ...`) such that
    they operate on MetaModes. This was the behavior in NVIDIA X driver versions 295.xx and
    earlier, but 302.xx releases altered the handling of these RandR 1.0/1.1 requests to
    operate on a single RandR output's modes.
  * With the above changes to IncludeImplicitMetaModes and RandR 1.0/1.1 handling, fullscreen
    applications (e.g., SDL-based applications, Wine), should have more resolutions available
    to them, and should interact better with multiple monitor configurations.
  * Fixed a bug that could cause G8x, G9x, and GT2xx GPUs to display a black screen or
    corruption after waking up from suspend.
  * Fixed several bugs that could cause some OpenGL programs to hang when calling fork(3).
  * Fixed an nvidia-settings bug that caused the results of ProbeDisplays queries made with
    the --display-device-string option to be formatted incorrectly.
  * Improved the responsiveness of updates to the nvidia-settings control panel when displays
    are hotplugged.
  * Fixed a bug that caused display corruption when setting some transforms, especially when
    panning a transformed display.
  * Fixed a bug that caused extra RandR events to be generated the first time a display is
    hotplugged.
  * Fixed a bug that caused X11 modelines with '@' in their names to be rejected.
  * Added support for DisplayPort 1.2 branch devices, which allow multiple displays to be
    connected to a single DisplayPort connector on a graphics board.
  * Fixed a bug that caused most OpenGL texture uploads to be slow when the context was bound
    rendering to an RGB overlay drawable.
  * Fixed a bug that caused audio over HDMI to not work after restarting the X server on some
    MCP7x (IGP) GPUs.
  * Updated the X configuration option UseDisplayDevice to honor the value none on any GPU.
  * Added support for DKMS in nvidia-installer. Installing the kernel module through DKMS allows
    the module to be rebuilt automatically when changing to a different Linux kernel. See the
    README and the nvidia-installer help text for the --dkms option.
  * Added RandR output properties _ConnectorLocation, ConnectorNumber, ConnectorType, EDID, _GUID,
    and SignalFormat. See the README for details on these properties.
  * Extended support for Base Mosaic to all G80+ SLI configurations with up to three displays.
  * Fixed a bug that caused some monitors to fail to wake from DPMS suspend mode when multiple
    DisplayPort monitors were attached to one GPU.
  * Removed controls for XVideo attributes from the "X Server XVideo Settings" page of the
    nvidia-settings control panel. XVideo attributes can be configured in XVideo player applications,
    or through utilities such as xvattr.
  * Fixed a bug that caused all ports on an XVideo adaptor to share color correction settings.
  * Removed support for the following X configuration options:
    SecondMonitorHorizSync
    SecondMonitorVertRefresh
    Similar control is available through the NVIDIA HorizSync and VertRefresh X configuration options.
    Please see the NVIDIA driver README for details.
  * Fixed a bug that prevented NVIDIA 3D Vision Pro from working properly when switching between
    X servers on different VTs.
* Tue Jun 19 2012 bumblebee-project@hotmail.com
- Update to 302.17
  * Added support for the following GPUs:
    GeForce GT 620M
    GeForce GT 640M
    GeForce GT 640M LE
    GeForce GT 650M
    GeForce GTX 660M
    GeForce GTX 670M
    GeForce GTX 675M
    GeForce GTX 555
    GeForce GTX 560 SE
    GeForce GT 415
    GeForce GTX 460 v2
    NVS 5400M
    NVS 310
    Quadro 410
  * Made nvidiaXineramaInfoOrder consistent with the RRSetOutputPrimary and
    RRGetOutputPrimary RandR requests: changes to either nvidiaXineramaInfoOrder or
    RandR OutputPrimary will be reflected in the other.
  * Fixed an interaction problem between RandR 1.2, ConstrainCursor, and panning that prevented
    panning from working properly.
  * Fixed a bug that caused RandR RRNotify_CrtcChange events to not be generated when switching
    between MetaModes with the same total size but different layout of display devices. This bug
    caused some window managers to not update their layouts in response to switching same-sized
    MetaModes.
  * Added support for desktop panning when rotation, reflection, or transformation is applied
    to a display device (either through RandR or through the MetaMode syntax); panning would
    previously be ignored in that case.
  * Added an "EDID" property to RandR 1.2 outputs. This property contains the binary contents of
    the connected monitor's extended display identification data, which allows applications such as
    the GNOME display properties dialog to query information about it.
  * Fixed a bug that caused audio over HDMI to not work on some GPUs after querying the RandR
    configuration (e.g., `xrandr -q`).
  * Added the "nvidiaXineramaInfo" X configuration option to report the layout of multiple display
    devices within an X screen. This is enabled by default. When disabled on X servers with
    RandR 1.2 support, the NVIDIA X driver will report one screen-sized region. When disabled on
    X servers without RandR 1.2 support, no Xinerama information will be reported. For backwards
    compatibility, the "NoTwinViewXineramaInfo" option disables nvidiaXineramaInfo.
  * Added the "nvidiaXineramaInfoOrder" X configuration option as a replacement for
    "TwinViewXineramaInfoOrder". For backwards compatibility, "TwinViewXineramaInfoOrder" is kept as
    a synonym for "nvidiaXineramaInfoOrder".
  * Added the "nvidiaXineramaInfoOverride" X configuration option as a replacement for
    "TwinViewXineramaInfoOverride". For backwards compatibility, "TwinViewXineramaInfoOverride" is kept
    as a synonym for "nvidiaXineramaInfoOverride".
  * Fixed a bug that prevented the use of some SLI Mosaic topologies.
  * Added the "MetaModeOrientation" X configuration option as a replacement for "TwinViewOrientation".
    "TwinViewOrientation" is kept as a synonym for "MetaModeOrientation", for backwards compatibility.
  * Disabled the use of certain OpenGL optimizations with Autodesk Maya and Mudbox, due to conflicts
    between these applications and the optimizations. Some performance loss in Autodesk Maya and
    Mudbox is possible, as a result.
  * Fixed a behavior issue where redundant DPMS state transitions were leading to unexpected screen
    blanking on DisplayPort displays.
* Wed Jun 13 2012 bumblebee-project@hotmail.com
- Update to 295.59
  * Added support for the following GPUs:
    NVS 5400M
    NVS 310
    GeForce GT 620M
    GeForce GT 640M
    GeForce GT 640M LE
    GeForce GT 650M
    GeForce GTX 660M
    GeForce GTX 670M
    GeForce GTX 675M
    GeForce GTX 555
    GeForce GTX 560 SE
    GeForce GT 415
    GeForce GTX 460 v2
  * Disabled the use of certain OpenGL optimizations with Autodesk Maya and Mudbox, due to
    conflicts between these applications and the optimizations. Some performance loss in
    Autodesk Maya and Mudbox is possible, as a result.
  * Fixed a behavior issue where redundant DPMS state transitions were leading to unexpected
    screen blanking on DisplayPort displays.
* Thu May 31 2012 bumblebee-project@hotmail.com
- Update to 302.11
  * Added support for the following GPUs:
    GeForce GTX 690
    GeForce GTX 670
    GeForce 605
    GeForce GT 610
    GeForce GT 630
    GeForce GT 640
    GeForce GT 645
  * Fixed a bug affecting some G-Sync configurations which could cause active stereo content to be
    inverted on some display devices.
  * Added support for calculating the physical size and DPI of each RandR 1.2 Output using the
    EDID Detailed Timing Description.
  * Fixed a bug that prevented a workaround for the invalid EDID in certain AUO laptop flat panels
    from being applied, leading to an 800x600 desktop repeated several times across the screen.
  * Fixed a bug that caused the link configuration of DisplayPort devices to be reported incorrectly
    in nvidia-settings.
* Thu May 31 2012 bumblebee-project@hotmail.com
- Update to 295.53
  * Added support for the following GPU:
    GeForce GTX 670
    GeForce 605
    GeForce GT 610
    GeForce GT 630
    GeForce GT 640
    GeForce GT 645
  * Fixed a bug affecting some G-Sync configurations which could cause active stereo content to be
    inverted on some display devices.
* Sat May  5 2012 bumblebee-project@hotmail.com
- Update to 302.07
  * Fixed a bug that caused OpenGL programs to leak file descriptors when calling exec().
  * Fixed rendering corruption at the start of new X server generation.
  * Added X driver support for RandR 1.2 and RandR 1.3.
    See "Support for the X Resize and Rotate Extension" in the README for details.
  * Extended the MetaMode X configuration option syntax with the following new attributes:
    Rotation : specifies the display device's rotation
    Reflection : specifies the display device's reflection
    Transform : specifies a 3x3 transformation matrix to be applied to the display device
    ViewPortOut : specifies the region of the mode in which to display pixels
    ViewPortIn : specifies the size of the region in the X screen to display in the ViewPortOut
    For example, "DFP-0: nvidia-auto-select { Rotation=left }".
    See "Configuring Multiple Display Devices on One X Screen" in the README for details.
  * Removed the TwinView X configuration option; the functionality it provided is now enabled by default.
    Previously, the NVIDIA X driver only enabled one display device for an X screen unless TwinView was
    enabled. Now, the NVIDIA X driver enables, by default, as many display devices as the GPU supports
    driving simultaneously. To limit how many display devices are driven by an X screen,
    use the UseDisplayDevice X configuration option.
  * Added a CurrentMetaMode attribute to the nvidia-settings command line,
    to query and set the current MetaMode.
    As an example, these two commands are equivalent:
    xrandr --output DVI-I-2 --mode 1280x1024 --pos 0x0 --output DVI-I-3 --mode 1920x1200 --pos 1280x0
    nvidia-settings --assign CurrentMetaMode="DVI-I-2: 1280x1024 +0+0, DVI-I-3: 1920x1200 +1280+0"
  * Removed overscan compensation configurability from NV-CONTROL and nvidia-settings. This can be
    configured, with finer granularity, through the ViewPortIn and ViewPortOut MetaMode attributes.
    See "Configuring Multiple Display Devices on One X Screen" in the README for details.
  * Altered mode validation such that for digital display devices the X driver only allows, by default,
    modes which are reported in the EDID. Previously, the NVIDIA X driver allowed other modes,
    but implicitly scaled those other modes to one of the EDID modes.
    Now, only the modes in the EDID are validated and the X driver does not do any implicit scaling.
    Any desired scaling can be configured explicitly through the new ViewPortIn and
    ViewPortOut MetaMode attributes.
    See "Configuring Multiple Display Devices on One X Screen" in the README for details.
  * Removed Flat Panel Scaling configurability in nvidia-settings. Any desired scaling can be
    configured through the new ViewPortIn and ViewPortOut MetaMode attributes.
  * Hotplug events (specifically, the RRNotify_OutputChange RandR event) are now generated when
    display devices are connected and disconnected from the GPU. Many desktop environments
    automatically resize the X desktop in response to these events.
  * Added display device name aliases, such that X configuration options that use display device
    names can refer to a display device by one of several names, including the RandR Output name
    for the display device. The X log reports the list of aliases for each display device.
  * Updated EDID parsing to include more complete support for EDID 1.4 and more recent versions
    of CEA-861.
  * Removed the Rotate X configuration option. This was used to statically rotate the X screen.
    Its functionality is replaced by the Rotation MetaMode attribute and RandR 1.2 rotation support.
    See the README for details.
  * Removed the RandRRotation X configuration option. This enabled configurability of X screen
    rotation via RandR 1.1. Its functionality is replaced by the Rotation MetaMode attribute and
    RandR 1.2 rotation support. See the README for details.
  * Removed support for the following NV-CONTROL attributes:
    NV_CTRL_GPU_SCALING
    NV_CTRL_GPU_SCALING_DEFAULT_TARGET
    NV_CTRL_GPU_SCALING_DEFAULT_METHOD
    NV_CTRL_DFP_SCALING_ACTIVE
    NV_CTRL_GPU_SCALING_ACTIVE
    NV_CTRL_FRONTEND_RESOLUTION
    NV_CTRL_BACKEND_RESOLUTION
    NV_CTRL_OVERSCAN_COMPENSATION
    NV_CTRL_FLATPANEL_BEST_FIT_RESOLUTION
  * Improved rendering performance for RENDER bitmap text.
  * Enabled the OpenGL "Sync to VBlank" option by default.
  * Added a new option, --restore-original-backup, to nvidia-xconfig. nvidia-xconfig creates a
    backup of the original X configuration file when modifying an X configuration file that does not
    appear to have been previously modified by nvidia-xconfig. This option restores a backup of the
    original X configuration file, if such a backup is found.
  * Expose the following additional FSAA modes via NV-CONTROL, nvidia-settings, and through X visuals
    and GLXFBConfigs:
    16X multisample FSAA on all GeForce GPUs
    Coverage sample FSAA on G80 and above GeForce GPUs
    32X multisample FSAA on G80 and above Quadro GPUs
    64X multisample FSAA on Fermi and above Quadro GPUs
  * Enabled conformant texture clamping by default in OpenGL.
  * Removed support for the GVO Clone mode NV-CONTROL attributes:
    NV_CTRL_GVO_DISPLAY_X_SCREEN
    NV_CTRL_GVO_X_SCREEN_PAN_X
    NV_CTRL_GVO_X_SCREEN_PAN_Y
  * Added a new, higher resolution icon for nvidia-settings.
  * Updated the NVIDIA X driver's handling of X configuration options that affect an entire GPU,
    not just a particular X screen running on a GPU (e.g., NoPowerConnectorCheck):
    for such X configuration options, the X driver will now honor the option on any of
    the X screens configured on the GPU. Prior to this change, the NVIDIA X driver only honored
    such options on the first X screen configured on a GPU.
  * Added a checkbox to nvidia-settings to control the texture clamping attribute. When the box is
    checked, OpenGL textures are clamped according to the OpenGL specification. When it is unchecked,
    GL_CLAMP is remapped to GL_CLAMP_TO_EDGE for borderless 2D textures.
  * Removed the "Display" and "X Screen" tabs from the "X Server Display Configuration Page" of
    nvidia-settings, and added a new "Selection" dropdown menu for selecting X screens or display
    devices. This makes it easier to select X screens/Displays that are hidden.
  * Fixed a problem where starting, stopping, and moving OpenGL application windows was very slow
    on Quadro FX 4600, Quadro FX 5600, GeForce 8800 GTX, GeForce 8800 GTS, and GeForce 8800 Ultra.
  * Fixed an OpenGL performance regression which affected Geforce 6 and Geforce 7 series integrated GPUs.
* Sat May  5 2012 bumblebee-project@hotmail.com
- Update to 295.49
  * Added support for the following GPU:
    GeForce GTX 690
  * Fixed a problem where starting, stopping, and moving OpenGL application windows was very slow on
    Quadro FX 4600, Quadro FX 5600, GeForce 8800 GTX, GeForce 8800 GTS, and GeForce 8800 Ultra.
  * Fixed an OpenGL performance regression which affected Geforce 6 and Geforce 7 series integrated GPUs.
* Thu Apr 12 2012 bumblebee-project@hotmail.com
- Update to 295.40
  * Closed a security vulnerability which made it possible for attackers to reconfigure GPUs
    to gain access to arbitrary system memory. For further details,
    see: http://nvidia.custhelp.com/app/answers/detail/a_id/3109
  * Fixed a bug that caused DisplayPort devices to occasionally fail to turn back on after
    the system is resumed from suspend.
  * Added a ModeValidation X configuration option token, "AllowNon3DVisionModes", to allow modes
    that are not optimized for NVIDIA 3D Vision to be validated on 3D Vision monitors.
  * Added support for the following GPUs:
    GeForce GT 635M
    GeForce GT 610
* Sun Apr  1 2012 bumblebee-project@hotmail.com
- Update to 295.33
  * Added support for the following GPUs:
    GeForce GTX 680
    GeForce GT 630M
    GeForce GT 620
  * Fixed a VDPAU bug where decoding some H.264 streams would cause hardware errors on lower-end products,
    resulting in corruption and poor performance.
  * Fixed a bug that caused DisplayPort audio to stop working after monitors are hotplugged on GeForce GT 520.
  * Improved compatibility with recent Linux kernels.
  * Fixed a behavior change that prevented ConnectedMonitor from being usable with DisplayPort connectors.
  * Marked the GVO Clone mode NV-CONTROL attributes:
    NV_CTRL_GVO_DISPLAY_X_SCREEN
    NV_CTRL_GVO_X_SCREEN_PAN_X
    NV_CTRL_GVO_X_SCREEN_PAN_Y
    as deprecated. They will be removed in a future release. To display an X screen over GVO,
    it is recommended to use GVO with MetaModes, instead.
  * Fixed a bug that caused DisplayPort devices to not be listed in Xorg.*.log. For example,
    if only DisplayPort devices are attached, the log file would contain
    Quote:
    (--) NVIDIA(0): Connected display device(s) on NVIDIA GPU at PCI:2:0:0
    (--) NVIDIA(0): none
  * Added support for 3D Vision ready displays that have a NVIDIA 3D Vision infrared emitter
    built inside the panel itself.
  * Fixed a bug that caused OpenGL applications to crash with some libc versions, such as eglibc 2.15.
  * Fixed a bug that caused HDMI audio to stop working on AppleTV devices when an X server was started.
* Thu Feb 16 2012 bumblebee-project@hotmail.com
- Update to 295.20
  * Fixed a bug that caused black areas to appear on the back faces of some models in Maya.
  * Fixed a bug that resulted in the printing of spurious loader error messages.
  * Fixed a bug that could cause X to crash after hotplugging displays.
  * Fixed a bug which caused face selections to be misrendered in Maya when using the paint selection tool.
  * Improved performance for interactive tools in Mudbox.
  * Added a "--no-opengl-files" option to nvidia-installer to allow installation of the driver without OpenGL files that might conflict with already installed OpenGL implementations.
  * Split the DFP configuration page in nvidia-settings into multiple tabs, allowing the controls to be displayed on smaller screens.
* Fri Feb 10 2012 bumblebee-project@hotmail.com
- Update to 295.17
  * Fixed a bug that prevented the internal panel from working on some laptops with GeForce 7 series GPUs.
  * Added support for xserver 1.11.99.901 (also known as 1.12 RC1).
* Mon Jan  2 2012 bumblebee-project@hotmail.com
- Update to 295.09
  * Added support for the following GPU:
  * Tesla X2090
  * Fixed an OpenGL bug where using display lists on Fermi-based GPUs could result in missing rendering in some cases.
  * Fixed an OpenGL bug that caused incorrect rendering when using framebuffer objects to render to 16-bit color textures with alpha.
  * Fixed two bugs that caused sporadic application crashes in some multi-threaded OpenGL applications.
  * Fixed a bug that caused creating OpenGL 4.2 contexts with glXCreateContextAttribsARB to fail.
  * Fixed a bug that caused OpenGL to print
    Xlib: extension "NV-GLX" missing on display ":0".
    when used with a non-NVIDIA implementation of the GLX X extension.
  * Implemented color depth 30 (10 bits per component) support for GeForce 8 series and higher GPUs.
  * Implemented support for constraining cursors to the visible regions of connected displays; see the "ConstrainCursor" X Option in the README for details.
  * Fixed a bug that would cause Firefox to abort on pages with Flash when layers acceleration was force-enabled on Linux and Solaris.
* Thu Dec  8 2011 bumblebee-project@hotmail.com
- Update to 290.10
  * Fixed a bug that would cause OpenGL applications to crash when run with recent releases of glibc such as glibc 2.14.90.
  * Improved the performance of FBO bind operations when using Xinerama by ~30%% in some cases.
  * Fixed a bug that could cause stereo corruption when driving a stereo display and a non-stereo display from the same GPU.
  * Fixed a bug that could cause display devices on a secondary GPU to get swapped between X screens when restarting the X server.
  * Fixed a bug that could result in line flickering in full-scene anti- aliasing contexts.
  * Fixed a bug that caused the physical dimensions of rotated monitors to be reported incorrectly.
  * Add support for the pre-VBO DrawArrays command in the server-side GLX driver module. The NVIDIA client-side GLX implementation never sends this command, but the server needs to support it for compatibility with other GLX client implementations.
  * Fixed a regression that caused blank/white windows when exhausting video memory on GeForce 6 and 7 series GPUs while using composited desktops.
  * Fixed a bug that caused a crash when glDrawArrays was used with a non-VBO vertex attribute array to draw on a Xinerama screen other than screen 0 using an indirect GLX context.
* Tue Oct 25 2011 bumblebee-project@hotmail.com
- Update to 290.03
  * Added support for the following GPU:
    GeForce 510
  * Fixed a bug that prevented the driver from loading on some systems with integrated graphics.
  * Fixed issues in VDPAU that prevented allocating and displaying extremely large VdpOutputSurfaces.
  * Added support for limiting heap allocations in the OpenGL driver through the use of the __GL_HEAP_ALLOC_LIMIT environment variable. See the README for further details.
  * Added an "Accel" option to the X driver to allow disabling its use of the graphics processing hardware. This is useful when other components, such as CUDA, require exclusive use of the GPU's processing cores.
  * Modified how the OpenGL driver allocates executable memory so it may continue to function properly if /tmp is mounted noexec. As some fallback allocation methods may be prohibited under SELinux policy, the driver now supports detection of this policy as well as manual override of this detection via the __GL_SELINUX_BOOLEANS environment variable.
  * Fixed a bug that caused various GLSL built-in uniforms to not be updated properly when calling glPopAttrib.
  * Improved performance by caching compiled OpenGL shaders to disk. Added a "GLShaderDiskCache" option to the X driver to enable/disable this feature. Added the __GL_SHADER_DISK_CACHE and __GL_SHADER_DISK_CACHE_PATH environment variables for further configuration. See the README for further details.
  * Fixed a bug that caused trapezoid and triangle rendering to be very slow on older GPUs with xorg-server 1.11.
* Sat Oct  8 2011 bumblebee-project@hotmail.com
- Update to 285.05.09
  * Added support for the following GPU:
    GeForce GT 520MX
  * Added support for xserver ABI 11 (xorg-server 1.11).
  * Fixed a bug causing a Linux kernel BUG when retrieving CPU information on some systems.
  * Fixed a bug causing some applications to hang on exit.
  * Fixed a bug causing flickering in some GPU/display combinations.
  * Fixed a bug that could result in poor OpenGL performance after hotplugging a monitor.
  * Fixed a bug causing possible text corruption when recovering from GPU errors.
* Sun Sep 25 2011 bumblebee-project@hotmail.com
- Initial release.
