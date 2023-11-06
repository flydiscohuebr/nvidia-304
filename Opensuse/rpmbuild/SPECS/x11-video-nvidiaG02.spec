#
# spec file for package x11-video-nvidiaG02
#
# Copyright (c) 2017 SUSE LINUX Products GmbH, Nuernberg, Germany.
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

%if 0%{?suse_version} > 1010 || "%_repository" == "SLE_10_XORG7"
%define xlibdir %{_libdir}/xorg
%else
%define xlibdir %{_prefix}/X11R6/%{_lib}
%endif

%if 0%{?suse_version} < 1130
%define GENERATE_IDENTITY_MAP 1
%else
%define GENERATE_IDENTITY_MAP 0
%endif

%if 0%{?suse_version} >= 1315
%define xmodulesdir %{xlibdir}/modules
%else
%define xmodulesdir %{xlibdir}/modules/updates
%endif

Name:           x11-video-nvidiaG02
Version:        304.137
Release:        lp155.1.1
License:        SUSE-NonFree
Summary:        NVIDIA graphics driver for GeForce 6xxx and newer GPUs
URL:            https://www.nvidia.com/object/unix.html
Group:          System/Libraries
Source0:        NVIDIA-Linux-x86-%{version}.run
Source1:        NVIDIA-Linux-x86_64-%{version}.run
Source2:        pci_ids-%{version}.new
Source3:        nvidia-settings.desktop
Source4:        fetch.sh
Source5:        README
Source6:        Xwrapper
Source7:        pci_ids-%{version}
Source8:        rpmlintrc
Source9:        libvdpau-0.4.tar.gz
Source10:       vdpauinfo-0.0.6.tar.gz
Source11:       modprobe.nvidia
Source12:       pci_ids-%{version}.legacy
Patch:          vdpauinfo-missing-lX11.diff
Patch1:         U_Use-secure_getenv-3-to-improve-security.patch
BuildRequires:  update-desktop-files
%if 0%{?suse_version} < 1130
BuildRequires:  doxygen
BuildRequires:  gcc-c++
BuildRequires:  graphviz
BuildRequires:  pkgconfig
BuildRequires:  texlive
BuildRequires:  xorg-x11-devel
%endif
%if 0%{?suse_version} < 1020
BuildRequires:  xorg-x11-compat70-devel
%endif
Requires:       nvidia-computeG02 = %{version}
Provides:       nvidia_driver = %{version}
Conflicts:      x11-video-nvidia
Conflicts:      x11-video-nvidiaG01
Conflicts:      fglrx_driver
Requires:       libvdpau1
%if 0%{?suse_version} >= 1315
Requires(post):   update-alternatives
Requires(postun): update-alternatives
# on Optimus we want to switch back to X.Org's libglx.so (bsc#1111471)
Requires(post):   xorg-x11-server
%endif
# needed for Optimus systems once NVIDIA's libs get disabled (our default);
# these packages won't get installed when adding NVIDIA's repository before
# the installation, which e.g. happens on SLED (bsc#1111471)
Recommends:     Mesa-libGL1
Recommends:     Mesa-libEGL1
Recommends:     Mesa-libGLESv1_CM1
Recommends:     Mesa-libGLESv2-2
ExclusiveArch:  %ix86 x86_64
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
This package provides the closed-source NVIDIA graphics driver
for GeForce 6xxx and newer GPUs.

%package -n nvidia-computeG02
Summary:        NVIDIA driver for computing with GPGPU
Group:          System/Libraries
# to provide a hint about split to zypper dup:
Provides:       x11-video-nvidiaG02:/usr/lib/libcuda.so
Conflicts:      libOpenCL1

%description -n nvidia-computeG02
NVIDIA driver for computing with GPGPUs using CUDA or OpenCL.

%package -n libvdpau1
License:        X11/MIT
Summary:        VDPAU wrapper and trace libraries
Group:          System/Libraries

%description -n libvdpau1
This package contains the libvdpau wrapper library and the
libvdpau_trace debugging library, along with the header files needed to
build VDPAU applications.  To actually use a VDPAU device, you need a
vendor-specific implementation library.  Currently, this is always
libvdpau_nvidia.  You can override the driver name by setting the
VDPAU_DRIVER environment variable.

%package -n libvdpau-devel
License:        X11/MIT
Summary:        VDPAU wrapper development files
Group:          Development/Libraries/X11
Requires:       libvdpau1

%description -n libvdpau-devel
Note that this package only contains the VDPAU headers that are
required to build applications. At runtime, the shared libraries are
needed too and may be installed using the proprietary nVidia driver
packages.

%package -n libvdpau_trace1
License:        X11/MIT
Summary:        VDPAU trace library
Group:          System/Libraries
Requires:       libvdpau1

%description -n libvdpau_trace1
This package provides the library for tracing VDPAU function calls.

%prep
%setup -T -c %{name}-%{version}
%ifarch %ix86
 sh %{SOURCE0} -x
%endif
%ifarch x86_64
 sh %{SOURCE1} -x
%endif
%if 0%{?suse_version} < 1130
tar xvf %{SOURCE9}
tar xvf %{SOURCE10}
pushd vdpauinfo-*
%patch -p0
popd
pushd libvdpau-*
%patch1 -p1
popd
%endif

%build
# nothing

%install
# no longer alter, i.e. strip NVIDIA's libraries
export NO_BRP_STRIP_DEBUG=true
%if 0%{?suse_version} < 1130
pushd libvdpau-*
  %configure
  make %{?jobs:-j%jobs}
  %makeinstall
  rm %{buildroot}%{_libdir}/libvdpau.la
  rm %{buildroot}%{_libdir}/vdpau/libvdpau_trace.la
popd
%endif
cd NVIDIA-Linux-x86*-%{version}
# would be nice if it worked ...
#./nvidia-installer \
#	--accept-license \
#	--expert \
#	--no-questions \
#	--ui=none \
#	--no-precompiled-interface \
#	--no-runlevel-check \
#	--no-rpms \
#	--no-backup \
#	--no-network \
#	--no-recursion \
#	--no-kernel-module \
#	--log-file-name=$PWD/log \
#	--x-prefix=%{buildroot}%{_prefix}/X11R6 \
#	--opengl-prefix=%{buildroot}%{_prefix} \
#	--utility-prefix=%{buildroot}%{_prefix}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_prefix}/X11R6/lib
install -d %{buildroot}%{_prefix}/lib/tls
install -d %{buildroot}%{_prefix}/X11R6/%{_lib}
install -d %{buildroot}%{_libdir}/tls
install -d %{buildroot}%{_prefix}/X11R6/%{_lib}/tls
install -d %{buildroot}%{_prefix}/lib/vdpau
install -d %{buildroot}%{_libdir}/vdpau
install -d %{buildroot}%{xmodulesdir}/drivers
install -d %{buildroot}%{xmodulesdir}/extensions
install -d %{buildroot}%{_sysconfdir}/OpenCL/vendors/
install nvidia-settings %{buildroot}%{_bindir}
install nvidia-bug-report.sh %{buildroot}%{_bindir}
install nvidia-xconfig %{buildroot}%{_bindir}
install nvidia-smi %{buildroot}%{_bindir}
install nvidia-debugdump %{buildroot}%{_bindir}
install nvidia-cuda-proxy-control %{buildroot}%{_bindir}
install nvidia-cuda-proxy-server %{buildroot}%{_bindir}
install tls/libnvidia-tls.so.* %{buildroot}%{_libdir}/tls
install libnvidia* %{buildroot}%{_libdir}
install libcuda* %{buildroot}%{_libdir}
install libOpenCL* %{buildroot}%{_libdir}
install libnvcuvid* %{buildroot}%{_libdir}
install libnvidia-ml* %{buildroot}%{_libdir}
install libvdpau_nvidia.so* %{buildroot}%{_libdir}/vdpau
# Bug #596481
ln -s vdpau/libvdpau_nvidia.so.1 %{buildroot}%{_libdir}/libvdpau_nvidia.so
# the GL lib from Mesa is in /usr/%{_lib} so we install in /usr/X11R6/%{_lib}
rm libGL.la
install libGL* %{buildroot}%{_prefix}/X11R6/%{_lib}
# still a lot of applications make a dlopen to the .so file
ln -snf libGL.so.1 %{buildroot}%{_prefix}/X11R6/%{_lib}/libGL.so
# same for libOpenGL/libcuda/libnvcuvid
ln -snf libOpenCL.so.1 %{buildroot}%{_libdir}/libOpenCL.so
ln -snf libcuda.so.1   %{buildroot}%{_libdir}/libcuda.so
ln -snf libnvcuvid.so.1 %{buildroot}%{_libdir}/libnvcuvid.so
# NVML library for Tesla compute products (new since 270.xx)
ln -s libnvidia-ml.so.1  %{buildroot}%{_libdir}/libnvidia-ml.so
%if 0%{?suse_version} < 1100
install libnvidia-wfb.so.%{version} \
  %{buildroot}%{xmodulesdir}
ln -sf libnvidia-wfb.so.%{version} %{buildroot}%{xmodulesdir}/libwfb.so
%endif
install nvidia_drv.so %{buildroot}%{xmodulesdir}/drivers
%if 0%{?suse_version} < 1315
install libglx.so.%{version} \
  %{buildroot}%{xmodulesdir}/extensions/
ln -sf libglx.so.%{version} %{buildroot}%{xmodulesdir}/extensions/libglx.so
%else
mkdir -p %{buildroot}%{xmodulesdir}/extensions/nvidia
install libglx.so.%{version} \
  %{buildroot}%{xmodulesdir}/extensions/nvidia/nvidia-libglx.so
%endif
install libXvMCNVIDIA* %{buildroot}%{_prefix}/X11R6/%{_lib}
chmod 644 %{buildroot}%{_prefix}/X11R6/%{_lib}/libXvMCNVIDIA.a
%ifarch x86_64
install 32/tls/libnvidia-tls.so.* %{buildroot}%{_prefix}/lib/tls
install 32/libnvidia* %{buildroot}%{_prefix}/lib
install 32/libcuda* %{buildroot}%{_prefix}/lib
install 32/libOpenCL* %{buildroot}%{_prefix}/lib
install 32/libvdpau_nvidia.so* %{buildroot}%{_prefix}/lib/vdpau
install 32/libGL* %{buildroot}%{_prefix}/X11R6/lib
# Bug #596481
ln -s vdpau/libvdpau_nvidia.so.1 %{buildroot}%{_prefix}/lib/libvdpau_nvidia.so
# still a lot of applications make a dlopen to the .so file
ln -snf libGL.so.1 %{buildroot}%{_prefix}/X11R6/lib/libGL.so
# same for libOpenGL/libcuda
ln -snf libOpenCL.so.1 %{buildroot}%{_prefix}/lib/libOpenCL.so
ln -snf libcuda.so.1   %{buildroot}%{_prefix}/lib/libcuda.so
%endif
install -d %{buildroot}%{_datadir}/doc/packages/%{name}
cp -a html %{buildroot}%{_datadir}/doc/packages/%{name}
install -m 644 LICENSE %{buildroot}%{_datadir}/doc/packages/%{name}
install -d %{buildroot}/%{_mandir}/man1
install -m 644 *.1.gz %{buildroot}/%{_mandir}/man1
%suse_update_desktop_file -i nvidia-settings System SystemSetup
install -d %{buildroot}%{_datadir}/pixmaps
install -m 644 nvidia-settings.png \
  %{buildroot}%{_datadir}/pixmaps
/sbin/ldconfig -n %{buildroot}%{_libdir}
/sbin/ldconfig -n %{buildroot}%{_libdir}/vdpau
/sbin/ldconfig -n %{buildroot}%{_prefix}/X11R6/%{_lib}
%ifarch x86_64
/sbin/ldconfig -n %{buildroot}%{_prefix}/lib
/sbin/ldconfig -n %{buildroot}%{_prefix}/lib/vdpau
/sbin/ldconfig -n %{buildroot}%{_prefix}/X11R6/lib
%endif
%if %GENERATE_IDENTITY_MAP
mkdir -p %{buildroot}%{_datadir}/sax/sysp/maps/update/ \
         %{buildroot}%{_datadir}/sax/api/data/cdb/ \
         %{buildroot}%{_localstatedir}/lib/hardware/ids
> %{buildroot}%{_datadir}/sax/sysp/maps/update/Identity.map.10.%{name}
> %{buildroot}%{_datadir}/sax/api/data/cdb/Cards.10.%{name}
> %{buildroot}%{_localstatedir}/lib/hardware/ids/10.%{name}
%if 0%{?suse_version} > 1100
%if 0%{?suse_version} > 1220
(cat %_sourcedir/pci_ids-%{version}.legacy; \
%else
(cat %_sourcedir/pci_ids-%{version}; \
%endif
%else
(cat %_sourcedir/pci_ids-%{version}.new; \
%endif
) | \
while read line; do
  VID=0x10de
  NAME=NVIDIA
  SERVER=nvidia
  DEVICE=$(echo $line|awk '{for (i=2;i<NF;i++) printf("%s ",$i); printf("%s",$NF)}')
  DID=$(echo $line|awk '{print $1}'|tr [[:upper:]] [[:lower:]] | sort -u)
  cat >> %{buildroot}%{_datadir}/sax/sysp/maps/update/Identity.map.10.%{name} << EOF
NAME=${NAME}&DEVICE=${DEVICE}&VID=${VID}&DID=${DID}&SERVER=${SERVER}&EXT=&OPT=&RAW=&PROFILE=&SCRIPT3D=&PACKAGE3D=&FLAG=DEFAULT
NAME=${NAME}&DEVICE=${DEVICE}&VID=${VID}&DID=${DID}&SERVER=${SERVER}&EXT=&OPT=&RAW=&PROFILE=&SCRIPT3D=&PACKAGE3D=&FLAG=3D
EOF
  cat >> %{buildroot}%{_datadir}/sax/api/data/cdb/Cards.10.%{name} << EOF
${NAME}:${DEVICE} {
 Driver    = ${SERVER}
 Flag      = 3D
 3DDriver  = ${SERVER}
}
EOF
  cat >> %{buildroot}%{_localstatedir}/lib/hardware/ids/10.%{name} << EOF
 vendor.id              pci ${VID}
&device.id              pci ${DID}
+device.name            ${DEVICE}
+driver.xfree           4|${SERVER}
+driver.xfree           4|${SERVER}|3d
EOF
echo >> %{buildroot}%{_localstatedir}/lib/hardware/ids/10.%{name}
done
%endif
%if 0%{?suse_version} > 1010
%if 0%{?suse_version} < 1330
install -m 755 $RPM_SOURCE_DIR/Xwrapper %{buildroot}%{_bindir}/X.%{name}
%endif
%else
mkdir -p %{buildroot}%{_prefix}/X11R6/bin
install -m 755 $RPM_SOURCE_DIR/Xwrapper %{buildroot}%{_prefix}/X11R6/bin/X.%{name}
%endif
install -m 644 nvidia.icd \
  %{buildroot}%{_sysconfdir}/OpenCL/vendors/
%if 0%{?suse_version} > 1140
# Create /etc/ld.so.conf.d/nvidia-gfxG02
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/nvidia-gfxG02.conf <<EOF
%{_prefix}/X11R6/%{_lib}
%ifarch s390x sparc64 x86_64 ppc64
%{_prefix}/X11R6/lib
%endif
%ifarch ppc
%{_prefix}/X11R6/lib64
%endif
EOF
%endif
%if 0%{?suse_version} < 1130
pushd ../vdpauinfo-*
%configure \
VDPAU_CFLAGS=-I$RPM_BUILD_ROOT/usr/include \
VDPAU_LIBS="-L%{_prefix}/X11R6/%{_lib} -L$RPM_BUILD_ROOT/%{_libdir} -lvdpau -lX11"
make %{?jobs:-j%jobs}
%makeinstall
popd
%endif
%if 0%{?suse_version} > 1230
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
install -m 644 $RPM_SOURCE_DIR/modprobe.nvidia %{buildroot}%{_sysconfdir}/modprobe.d/50-nvidia.conf
%endif

%post
# xorg.conf no longer been used since sle12
%if 0%{?suse_version} < 1120
if [ -f etc/X11/xorg.conf ]; then
  test -f etc/X11/xorg.conf.nvidia-post || \
    cp etc/X11/xorg.conf etc/X11/xorg.conf.nvidia-post
fi
# if configuration for proprietary driver already exists, bring it back
# (Bug #270040, comments #91/92)
if [ -f etc/X11/xorg.conf.nvidia-postun ]; then
  mv etc/X11/xorg.conf.nvidia-postun etc/X11/xorg.conf
fi
test -x usr/bin/switch2nvidia && usr/bin/switch2nvidia
# Bug #449486
if grep -q fbdev etc/X11/xorg.conf; then
  test -x usr/bin/nvidia-xconfig && usr/bin/nvidia-xconfig -s
fi
%endif
# Bug #345125
test -f %{xlibdir}/modules/drivers/nvidia_drv.so && \
  touch %{xlibdir}/modules/drivers/nvidia_drv.so
test -f %{xmodulesdir}/drivers/nvidia_drv.so && \
  touch %{xmodulesdir}/drivers/nvidia_drv.so
if ls var/lib/hardware/ids/* &> /dev/null; then
  >  var/lib/hardware/hd.ids
  for i in var/lib/hardware/ids/*; do
    cat $i >> var/lib/hardware/hd.ids
  done
fi
%if 0%{?suse_version} < 1330
test -f etc/sysconfig/displaymanager && \
. etc/sysconfig/displaymanager
if [ "${DISPLAYMANAGER_XSERVER}" == "X.%{name}" ]; then
  # broken entry in /etc/sysconfig/displaymanager:DISPLAYMANAGER_XSERVER
  # use a sane default instead
  DISPLAYMANAGER_XSERVER=Xorg
fi
%if 0%{?suse_version} > 1010
sed -i s/REPLACE_ME/${DISPLAYMANAGER_XSERVER}/g usr/bin/X.%{name}
%else
sed -i s/REPLACE_ME/${DISPLAYMANAGER_XSERVER}/g usr/X11R6/bin/X.%{name}
%endif
test -f etc/sysconfig/displaymanager && \
sed -i 's/DISPLAYMANAGER_XSERVER=.*/DISPLAYMANAGER_XSERVER=X.%{name}/g' \
       etc/sysconfig/displaymanager
%if 0%{?suse_version} > 1010
test -x /etc/X11/xdm/SuSEconfig.xdm && \
/etc/X11/xdm/SuSEconfig.xdm
%else
test -x /sbin/conf.d/SuSEconfig.xdm && \
SuSEconfig --module xdm
%endif
%endif
# Recreate initrd without KMS
%if 0%{?suse_version} < 1310
# Only touch config, if the use of KMS is enabled in initrd;
# known not to be required on openSUSE 13.1 (bnc#864701)
if grep -q NO_KMS_IN_INITRD=\"no\" /etc/sysconfig/kernel; then
  sed -i 's/NO_KMS_IN_INITRD.*/NO_KMS_IN_INITRD="yes"/g' /etc/sysconfig/kernel
  which mkinitrd && mkinitrd
fi
%endif
%if 0%{?suse_version} >= 1315
%_sbindir/update-alternatives \
    --force --install %{_libdir}/xorg/modules/extensions/libglx.so libglx.so %{_libdir}/xorg/modules/extensions/nvidia/nvidia-libglx.so 100
# make sure nvidia becomes the default (in case the link group is/was still in manual mode)
%_sbindir/update-alternatives \
      --set libglx.so %{_libdir}/xorg/modules/extensions/nvidia/nvidia-libglx.so
# On Optimus systems disable NVIDIA driver/libs completely by default (bnc#902667)
if lspci -n | grep -e '^..:..\.. 0300: ' | cut -d " "  -f3 | cut -d ":" -f1 | grep -q 8086; then
  %_sbindir/update-alternatives \
      --set libglx.so %{_libdir}/xorg/modules/extensions/xorg/xorg-libglx.so
  sed -i 's/\(^\/.*\)/#\1/g' %{_sysconfdir}/ld.so.conf.d/nvidia-gfxG02.conf
fi
%endif
/sbin/ldconfig
exit 0

%postun
/sbin/ldconfig
if [ "$1" -eq 0 ]; then
# switch2nv/switch2nv no longer available/needed since sle12
%if 0%{?suse_version} < 1120
  test -x usr/bin/switch2nv && usr/bin/switch2nv
%endif
  if ls var/lib/hardware/ids/* &> /dev/null; then
    >  var/lib/hardware/hd.ids
    for i in var/lib/hardware/ids/*; do
      cat $i >> var/lib/hardware/hd.ids
    done
  else
    rm -f var/lib/hardware/hd.ids
  fi
# xorg.conf no longer been used since sle12
%if 0%{?suse_version} < 1120
  test -f etc/X11/xorg.conf && \
    cp etc/X11/xorg.conf etc/X11/xorg.conf.nvidia-postun
  if [ -r etc/X11/xorg.conf.nvidia-post ]; then
    mv etc/X11/xorg.conf.nvidia-post etc/X11/xorg.conf
%if 0%{?suse_version} < 1130
  else
    sax2 -a -r
%endif
  fi
%endif
  if test -x /opt/gnome/bin/gnome-xgl-switch; then
    /opt/gnome/bin/gnome-xgl-switch --disable-xgl
  elif test -x /usr/bin/xgl-switch; then
    /usr/bin/xgl-switch --disable-xgl
  fi
  # Make sure that after driver uninstall /var/lib/X11/X link points
  # to a valid Xserver binary again (bnc#903732)
%if 0%{?suse_version} > 1010
%if 0%{?suse_version} < 1330
  test -x /etc/X11/xdm/SuSEconfig.xdm && \
  /etc/X11/xdm/SuSEconfig.xdm
%endif
%else
  test -x /sbin/conf.d/SuSEconfig.xdm && \
  SuSEconfig --module xdm
%endif
fi
# recreate initrd with KMS on openSUSE 13.1 (bnc#864701)
%if 0%{?suse_version} >= 1310
which mkinitrd && mkinitrd
%endif
%if 0%{?suse_version} >= 1315
if [ "$1" = 0 ] ; then
    # Avoid accidental removal of G<n+1> alternative (bnc#802624)
    if [ ! -f %{_libdir}/xorg/modules/extensions/nvidia/nvidia-libglx.so.%{version} ]; then
	"%_sbindir/update-alternatives" --remove libglx.so %{_libdir}/xorg/modules/extensions/nvidia/nvidia-libglx.so.%{version}
    fi
fi
%endif
exit 0

%post -n nvidia-computeG02 -p /sbin/ldconfig

%postun -n nvidia-computeG02 -p /sbin/ldconfig

%post -n libvdpau1 -p /sbin/ldconfig

%postun  -n libvdpau1 -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc %{_datadir}/doc/packages/%{name}
%doc %{_mandir}/man1/*
%if 0%{?suse_version} > 1140
%config %{_sysconfdir}/ld.so.conf.d/nvidia-gfxG02.conf
%endif
%if 0%{?suse_version} > 1010
%if 0%{?suse_version} < 1330
%{_bindir}/X.%{name}
%endif
%else
%{_prefix}/X11R6/bin/X.%{name}
%endif
%{_bindir}/nvidia*
%exclude %{_bindir}/nvidia-smi
%if 0%{?suse_version} > 1310
%dir %{_prefix}/X11R6/
%dir %{_prefix}/X11R6/%{_lib}
%endif
%{_prefix}/X11R6/%{_lib}/lib*
%dir %{_libdir}/tls
%dir %{_libdir}/vdpau
%{_libdir}/tls/lib*
%{_libdir}/lib*
%{_libdir}/vdpau/*
%exclude %{_libdir}/libcuda.so*
%exclude %{_libdir}/libOpenCL.so*
%exclude %{_libdir}/libnvidia-ml.so*
%exclude %{_libdir}/libnvidia-opencl.so*
%ifarch x86_64
%if 0%{?suse_version} > 1310
%dir %{_prefix}/X11R6/lib
%endif
%{_prefix}/X11R6/lib/lib*
%dir %{_prefix}/lib/tls
%dir %{_prefix}/lib/vdpau
%{_prefix}/lib/tls/lib*
%{_prefix}/lib/lib*
%{_prefix}/lib/vdpau/*
%exclude %{_prefix}/lib/libcuda.so*
%exclude %{_prefix}/lib/libOpenCL.so*
%exclude %{_prefix}/lib/libnvidia-ml.so*
%exclude %{_prefix}/lib/libnvidia-opencl.so*
%endif
%if 0%{?suse_version} > 1010 || "%_repository" == "SLE_10_XORG7"
%dir %{xlibdir}
%endif
%dir %{xlibdir}/modules
%dir %{xmodulesdir}
%if 0%{?suse_version} < 1100
%{xmodulesdir}/libnvidia-wfb.so.%{version}
%{xmodulesdir}/libwfb.so
%endif
%{xmodulesdir}/drivers
%{xmodulesdir}/extensions
%{_datadir}/applications/*.desktop
%{_datadir}/pixmaps/*.png
%if %GENERATE_IDENTITY_MAP
%dir %{_datadir}/sax
%dir %{_datadir}/sax/api/
%dir %{_datadir}/sax/api/data
%dir %{_datadir}/sax/sysp
%dir %{_datadir}/sax/sysp/maps
%dir %{_localstatedir}/lib/hardware
%{_datadir}/sax/api/data/cdb/
%{_datadir}/sax/sysp/maps/update/
%{_localstatedir}/lib/hardware/ids/
%endif
%if 0%{?suse_version} < 1130
%exclude %{_libdir}/libvdpau.so
%exclude %{_libdir}/libvdpau.so.1*
%exclude %{_libdir}/vdpau/libvdpau_trace.so.1*
%endif
%if 0%{?suse_version} > 1230
%dir %{_sysconfdir}/modprobe.d
%config %{_sysconfdir}/modprobe.d/50-nvidia.conf
%endif

%files -n nvidia-computeG02
%defattr(-,root,root)
%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%{_libdir}/libcuda.so*
%{_libdir}/libOpenCL.so*
%{_libdir}/libnvidia-ml.so*
%{_libdir}/libnvidia-opencl.so*
%{_bindir}/nvidia-smi
%ifarch x86_64
%{_prefix}/lib/libcuda.so*
%{_prefix}/lib/libOpenCL.so*
%{_prefix}/lib/libnvidia-ml.so*
%{_prefix}/lib/libnvidia-opencl.so*
%endif

%if 0%{?suse_version} < 1130

%files -n libvdpau1
%defattr(-,root,root)
%dir %{_libdir}/vdpau
/usr/bin/vdpauinfo
%{_libdir}/libvdpau.so.1*

%files -n libvdpau-devel
%defattr(-,root,root)
%doc %{_datadir}/doc/libvdpau
%dir %{_libdir}/vdpau
%{_includedir}/vdpau
%{_libdir}/libvdpau.so
%{_libdir}/pkgconfig/vdpau.pc

%files -n libvdpau_trace1
%defattr(-,root,root)
%dir %{_libdir}/vdpau
%{_libdir}/vdpau/libvdpau_trace.so.1*

%endif

%changelog
* Sat Dec 26 2020 pascom@orange.fr
- Added the installers from nVidia (not provided in openSUSE).
* Fri Jun  5 2020 Stefan Dirsch <sndirsch@suse.com>
- no longer require 3ddiag, which is no longer needed at all ...
* Thu Mar 12 2020 Stefan Dirsch <sndirsch@suse.com>
- using /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G0X.conf now,
  so a driver series update (when user ignores the explicit driver
  series conflict!) no longer will result in no access to NVIDIA
  devices (boo#1165987)
* Mon Jan  6 2020 Stefan Dirsch <sndirsch@suse.com>
- added "azure" kernel flavor
* Mon Jul  8 2019 Stefan Dirsch <sndirsch@suse.com>
- kmp-post.sh/kmp-trigger.sh
  * exit with error code 1 from %%post/%%trigger, if kernel module
    build/install fails (boo#1131028)
* Tue Jul  2 2019 Stefan Dirsch <sndirsch@suse.com>
- no longer touch xorg.conf on suse >= sle12
* Thu Jun 13 2019 Stefan Dirsch <sndirsch@suse.com>
- making use of parallel builds with make's -j option
* Fri Oct 12 2018 sndirsch@suse.com
-let x11-video-nvidiaG02 %%post-require xorg-x11-server, since on
  Optimus we want to switch back to X.Org's libglx.so (bsc#1111471)
* Fri Oct 12 2018 sndirsch@suse.com
- let x11-video-nvidiaG02 recommend the following packages:
  * Mesa-libGL1
  * Mesa-libEGL1
  * Mesa-libGLESv1_CM1
  * Mesa-libGLESv2-2
  This is needed for Optimus systems once NVIDIA's GL libs get disabled
  (our default); these packages won't get installed when adding NVIDIA's
  repository before the installation, which e.g. happens on SLED
  (bsc#1111471)
* Sun Sep 23 2018 sndirsch@suse.com
-  xf86-video-nvidia-legacy-0010-kernel-4.14.patch
  * fixes build against Kernel 4.12 (used on sle12-sp4)
* Sun Sep 23 2018 sndirsch@suse.com
- no longer alter, i.e. strip NVIDIA's libraries
* Thu May 17 2018 sndirsch@suse.com
- workaround build failure of kernelrelease target on sle12-sp4
  (boo#1093333)
* Sat Sep 30 2017 sndirsch@suse.com
- update to driver release 304.137
  * Improved compatibility with recent Linux kernels.
  * Updated nvidia-installer to label kernel modules with SELinux
    file type 'modules_object_t'. Some system SELinux policies only
    permit loading of kernel modules with this SELinux file type.
  * Removed support for checking for and downloading updated driver
    packages and precompiled kernel interfaces from nvidia-installer.
    This functionality was limited to unencrypted ftp and http, and
    was implemented using code that is no longer actively maintained.
- adjusted NVIDIA_kernel-define_linux/NVIDIA_kernel-define_linux-x86.diff
- obsoletes u_gcc4.8.5.patch, nvidia-304-4.10.patch
- fixed %%kver macro
- some more specfile cleanup
* Fri Aug 18 2017 sndirsch@suse.com
- kmp-post.sh/kmp-post-old.sh
  * make sure kernel module gets generated into initrd during
    kmp installation
- x11-video-nvidiaG04.spec
  * %%post: only recreate initrd if needed (possibly on sle11)
- nvidia-gfxG04.spec
  * use trigger scripts for Leap 42.3/sle12-sp3; trigger
    in addition to %%post on uninstall of drm-kmp (boo#1053934)
- preamble
  * readded provides to drm-kmp on Leap 42.3/sle12-sp3, since
    otherwise NVIDIA KMP isn't autoselected :-(
* Mon Jun 19 2017 sndirsch@suse.com
- computeG02: added conflicts to libOpenCL1 (boo#1044948)
* Thu May 25 2017 sndirsch@suse.com
- removed/disabled Xwrapper for TW/sle15, since you can't rely any
  longer on a displaymanager running as root (bsc#1040699)
* Fri May 19 2017 sndirsch@suse.com
- fixed dependancies so nvidia-computeG02 can now be installed
  without x11-video-nvidiaG02 package
  * moved 32bit libnvidia-ml.so.* and libnvidia-opencl.so* from
    x11-video-nvidiaG02 to nvidia-computeG02 package
* Mon Apr 24 2017 toddrme2178@gmail.com
- Various spec file and rpmlint cleanups:
  * Improve descriptions
  * Add URL
  * Remove spurious obsoletes (higher versions don't necessarily
    replace lower ones due to dropped graphics card support).
  * Add %%config tags
  * Update year
  * Use versioning provides to avoid self-obsoletes.
* Thu Feb 16 2017 sndirsch@suse.com
- update to driver release 304.135
  * Added support for X.Org xserver ABI 23 (xorg-server 1.19)
  * Fixed a bug that allowed nvidia-installer to attempt loading
    kernel modules that were built against non-running kernels.
* Tue Dec 13 2016 sndirsch@suse.com
- update to driver release 304.134
  * Added support for X.Org xserver ABI 23 (xorg-server 1.19)
  * Fixed a bug that allowed nvidia-installer to attempt loading kernel
    modules that were built against non-running kernels.
* Mon Sep 26 2016 sndirsch@suse.com
- update to driver release 304.132
  * Added /var/log/dmesg to the list of paths which are searched by
    nvidia-bug-report.sh for kernel messages.
  * Fixed a bug that caused kernel panics when using the NVIDIA driver
    on v4.5 and newer Linux kernels built with CONFIG_DEBUG_VM_PGFLAGS.
  * Updated nvidia-installer to support ncurses version 6.x.
* Fri Nov 27 2015 sndirsch@suse.com
- update-alternatives for libglx.so:
  * make sure nvidia becomes the default (in case the link group
    is/was still in manual mode)
* Thu Nov 12 2015 sndirsch@suse.com
- update to driver release 304.131
  * Fixed a bug that could cause texture corruption in some OpenGL
    applications when video memory is exhausted by a combination of
    simultaneously running graphical and compute workloads.
  * Added support for X.Org xserver ABI 20 (xorg-server 1.18).
* Thu Sep  3 2015 sndirsch@suse.com
- update to driver release 304.128
  * Removed libvdpau and libvdpau_trace from the NVIDIA driver package.
    VDPAU is not supported on the legacy hardware supported on the
    release 304 legacy driver branch. The libvdpau_nvidia vendor library
    is still included, so users who wish to use VDPAU with newer hardware
    that still works with release 304 drivers may install libvdpau from
    packages provided by the OS vendor where available, or from the source
    code available at: http://people.freedesktop.org/~aplattner/vdpau/
  * Updated nvidia-installer to use modprobe(8) when leaving the NVIDIA
    kernel module loaded after installation, instead of insmod(8) or
    libkmod. This allows the kernel module to honor any configuration
    directives that apply to it in /etc/modprobe.d when it is loaded.
  * Fixed a bug that allowed console messages from the Linux kernel to be
    drawn over the user interface of nvidia-installer.
-  supersedes 304.125-kernel-4.0.patch
* Tue Sep  1 2015 sndirsch@suse.com
- U_Use-secure_getenv-3-to-improve-security.patch
  * VUL-0: CVE-2015-5198: libvdpau: incorrect check for security
    transition (bnc#943967)
  * VUL-0: CVE-2015-5199: libvdpau: directory traversal in dlopen
    (bnc#943968)
  * VUL-0: CVE-2015-5200: libvdpau: vulnerability in trace
    functionality (bnc#943969)
* Tue Jun 16 2015 sndirsch@suse.com
- added Obsoletes/Conflicts for G01 and older (bnc#802624)
* Mon Jun 15 2015 sndirsch@suse.com
-  avoid accidental removal of G<n+1> alternative (bnc#802624)
* Mon Feb  2 2015 sndirsch@suse.com
- added missing legacy pci_ids file
* Fri Dec  5 2014 mmarek@suse.cz
- update to driver release 304.125
  * Added support for X.Org xserver ABI 19 (xorg-server 1.17).
  * Improved compatibility with recent Linux kernels.
  * Implemented support for disabling indirect GLX context
    creation using the -iglx option available on X.Org server
    release 1.16 and newer.  Note that future X.Org server
    releases may make the -iglx option the default.  To re-enable
    support for indirect GLX on such servers, use the +iglx
    option.
  * Added the "AllowIndirectGLXProtocol" X config option.  This
    option can be used to disallow use of GLX protocol.  See
    "Appendix B. X Config Options" in the README for more
    details.
  * Updated nvidia-installer to install a file in the system's
    xorg.conf.d directory, when a sufficiently new X server is
    detected, to cause the X server to load the "nvidia" X driver
    automatically if it is started after the NVIDIA kernel module
    is loaded.
    This feature is supported in X.Org xserver 1.16 and higher
    when running on Linux 3.9 or higher with CONFIG_DRM enabled.
  * Updated nvidia-installer to log uninstallation to a separate
    file from the installation log, and to attempt uninstalling
    previous driver installations using the installer program
    from the previous installation, when available.
  * Updated nvidia-installer to avoid writing to non-zero offsets
    of sysctl files in /proc/sys/kernel.
* Mon Nov 17 2014 sndirsch@suse.com
- Xwrapper: bail out, if an existing module cannot be unloaded;
  this can happen if a second Xsession starts
* Thu Nov  6 2014 sndirsch@suse.com
- update to driver release 304.123 (bnc#bnc#904048)
  * Improved compatibility with recent Linux kernels.
  * Fixed a bug that could result in system instability while
    restoring the VGA console.
  * Fixed an interaction problem with xserver 1.15 that occasionally
    caused OpenGL applications to continue rendering when they are
    minimized or unmapped.
  * Updated nvidia-bug-report.sh to search the systemd journal for
    X server logs and messages from the NVIDIA kernel module.
  * Added support for X.org xserver ABI 18 (xorg-server 1.16).
  * Fixed a bug that caused corruption or blank screens on monitors
    that use EDID version 1.3 or older when they are connected via
    DisplayPort on graphics boards that use external DisplayPort
    encoders, such as the Quadro FX 4800.
* Wed Nov  5 2014 sndirsch@suse.com
- On Optimus systems disable NVIDIA driver/libs completely by
  default (bnc#902667)
* Wed Nov  5 2014 sndirsch@suse.com
- Make sure that after driver uninstall /var/lib/X11/X link points
  to a valid Xserver binary again (bnc#903732)
* Sat Aug 16 2014 sndirsch@suse.com
- fixed installation of libglx on %%suse_version < 1315 (regression)
* Fri Aug 15 2014 sndirsch@suse.com
- update-alternatives: get rid again of
  /usr/lib64/xorg/modules/extensions/libglx.so and ghost entry for
  /etc/alternatives/libglx.so; it's sufficient to have this in
  xorg-x11-server package
* Wed Aug 13 2014 sndirsch@suse.com
- nvidia-glxG03:
  * added /etc/alternatives/libglx.so as ghost
  * moved libglx-nvidia.so to nvidia/nvidia-libglx.so to avoid
  messup in case anybody runs ldconfig in modules/extensions
* Mon Aug 11 2014 sndirsch@suse.com
- make use of update-alternatives for libglx.so (FATE#317822)
* Fri Aug  8 2014 sndirsch@suse.com
- no longer use "updates" X modules directory structure with sle12
  and openSUSE > 13.1 (FATE#317822)
* Tue Jun  3 2014 sndirsch@suse.com
- update to driver release 304.121
  * Improved compatibility with recent Linux kernels.
  * Fixed a bug that prevented the NVIDIA implementation of the
    Xinerama extension protocol requests from being used when RandR
    was enabled.
* Wed Mar 12 2014 sndirsch@suse.com
- enhanced rpmlintrc in order to to fix build on sle12
* Tue Feb 25 2014 sndirsch@suse.com
- update to driver release 304.119
  * Fixed a crash when using WebGL in Firefox with a Geforce 6 GPU.
- fixed %%if condition in specfile
* Tue Feb 25 2014 sndirsch@suse.com
- no longer touch NO_KMS_IN_INITRD sysconfig variable on openSUSE
  13.1 and recreate initrd in %%postun on openSUSE 13.1 (bnc#864701)
* Wed Feb 12 2014 sndirsch@suse.com
- enhanced rpmlintrc in order to to fix build on sle12
* Mon Feb 10 2014 sndirsch@suse.com
- with openSUSE > 13.1 and sle12 /usr/X11R6* directories need to be
  owned by the nvidia package itself
* Thu Jan 16 2014 sndirsch@suse.com
- update to driver release 304.117
  * added support for xorg-server 1.15
* Wed Oct  9 2013 sndirsch@suse.com
- update to driver release 304.108
  changes since version 304.88:
  * Implemented workarounds for two Adobe Flash bugs by applying libvdpau
    commit ca9e637c61e80145f0625a590c91429db67d0a40 to the version of libvdpau
    shipped with the NVIDIA driver.
  * Fixed a bug in nvidia-settings that could cause the wrong
    resolution to be set in basic mode for setups based on one
    display per X screen.
  * Added /usr/lib/modprobe.d to the list of directories where
    nvidia-installer may optionally install a generated modprobe
    configuration file to attempt to disable Nouveau.
* Tue Oct  8 2013 sndirsch@suse.com
- fixed SaX2 meta information for (open)SUSE > 12.2
* Tue Sep 10 2013 sndirsch@suse.com
- added modprobe options for NVIDIA kernel module, since these
  have been removed from xorg-x11-server package
* Thu Apr  4 2013 sndirsch@suse.com
- update to driver release 304.88
  * Fixed CVE-2013-0131: NVIDIA UNIX GPU Driver ARGB Cursor Buffer
    Overflow in "NoScanout" Mode.  This buffer overflow, which occurred
    when an X client installed a large ARGB cursor on an X server
    running in NoScanout mode, could cause a denial of service (e.g.,
    an X server segmentation fault), or could be exploited to achieve
    arbitrary code execution.
    For more details, see:
    http://nvidia.custhelp.com/app/answers/detail/a_id/3290
* Mon Mar 18 2013 sndirsch@suse.com
- update to driver release 304.84
  * Improved compatibility with recent Linux kernels.
  * Fixed a bug that could lead to rendering corruption after an X
    server generation (i.e., leaving an X server running after all
    of its clients have exited).
  * Removed a spurious dependency on libpangox from the nvidia-settings
    binary shipped as part of the driver package.
  * Fixed a bug that could cause the X server to crash when performing
    an RandR 1.0 rotation (e.g., `xrandr --orientation left`) after
    unplugging the last connected monitor.
  * Added support for X.org xserver ABI 14 (xorg-server 1.14).
  * Fixed font rendering performance and corruption problems on X servers with
    backported support for the new glyph cache functionality added to Pixman
    0.27.
  * Fixed a potential X server crash during initialization, when a
    graphics card with a TV connector has no TV connected.
  * Added a new X configuration option, "UseHotplugEvents", to allow the
    suppression of RandR events when adding or removing non-DisplayPort
    displays. See the "X Config Options" appendix of the README for details.
* Wed Jan  2 2013 sndirsch@suse.com
- moved libnvidia-opencl.so* to compute package
* Wed Nov  7 2012 sndirsch@suse.com
- update to driver release 304.64
  * Added a missing 32-bit compatibility library for libnvidia-opencl.so to
    the 64-bit Linux installer package.
  * Fixed a regression in backlight control functionality on some
    notebook configurations.
  * Fixed a performance issue with recent Linux kernels when allocating
    and freeing system memory.
  * Fixed a bug that sometimes prevented the display device / X screen
    selection menu from being displayed in nvidia-settings.
  * Fixed a bug that prevented X driver gamma manipulation from working
    after a VT-switch on some configurations.
  * Added the option "--output-file" to nvidia-bug-report.sh to allow
    specifying a custom filename for the log file.
  * Fixed a hang when using OpenGL programs with some SLI Mosaic
    configurations on pre-Fermi GPUs.
  * Added sections to the "Supported NVIDIA GPU Products" list for NVS,
    Tesla, and VGX products.
  * Added support for the following GPUs:
  * VGX K1
  * VGX K2
  * Tesla K20c
  * Tesla K20m
  * Fixed a bug that caused the EIZO FlexScan SX2762W monitor to remain blank
    when connected via DisplayPort.
  * Updated nvidia-settings to save and restore per-monitor color correction
    settings when RandR 1.2 or later is available.
  * Fixed a bug that caused too many display devices to appear in the X Screen
    page of nvidia-settings when SLI is enabled.
  * Fixed a bug that caused applications to stop rendering or the X server to
    hang in Xinerama configurations when windows were moved, resized, mapped,
    or unmapped.
  * Fixed a bug that caused poor OpenGL performance on GeForce 6 and 7 PCI
    cards.
  * Fixed a bug in nvidia-settings that made it report the status of ECC
    configuration incorrectly.
* Mon Oct 29 2012 sndirsch@suse.com
- update to driver release 304.60
  * Fixed a bug that caused the X server to crash if a display was put into
    DPMS off mode and subsequently reenabled while screen transformations are
    in use.
  * Fixed a bug that caused the X Resize and Rotate extension to be enabled
    when Xinerama is enabled.  These two X extensions are incompatible and
    having them both enabled can confuse window managers such as KDE's kwin.
    RandR is now correctly disabled when Xinerama is enabled.
  * Fixed a bug causing OpenGL stereo applications to not work properly
    when using passive stereo modes 5 through 9 on Quadro Fermi and newer
    GPUs.
  * Updated nvidia-settings to report Dedicated GPU Memory (i.e., the
    memory dedicated exclusively to the GPU) and Total GPU Memory (i.e.,
    Dedicated GPU Memory plus any TurboCache(TM)-accessible system memory)
    separately on the GPU information page.
  * Added reporting of the current utilization of Dedicated GPU Memory to
    the GPU information page of nvidia-settings.
  * Added support for the "Backlight" RandR output property for
    configuring the brightness of some notebook internal panels.
  * Fixed a bug that prevented the Ubuntu Unity launcher panel from
    unhiding: https://bugs.launchpad.net/unity/+bug/1057000
  * Fixed a bug that caused nvidia-installer to sometimes attempt
    to write a log file in a nonexistent directory.
  * Fixed a bug that caused incorrect input transformation after resizing
    an NVIDIA X screen with xserver ABI 12 (xorg-server 1.12) or newer.
  * Fixed a bug that caused GLX to leak memory when Xinerama is
    enabled.
  * Added support for the following GPUs:
  * GeForce GT 645M
  * GeForce GTX 670MX
  * GeForce GTX 675MX
  * GeForce GTX 650 Ti
  * Added support for the new Quadro Sync board for Quadro Kepler GPUs.
    See the "Configuring Frame Lock and Genlock" chapter in the README
    for details.
  * Fixed an X server crash on X.Org xserver 1.13 when it is compiled
    without support for DRI2.
  * Fixed a regression that broke color controls on older X servers.
  * Fixed a bug that sometimes caused the display layout area of the
    nvidia-settings control panel to be laid out incorrectly.
  * Fixed a bug that prevented panning from working correctly after a
    modeswitch on some X servers with support for cursor constraining.
  * Gamma ramp and colormap adjustments now apply correctly when screen
    transformations such as rotation and keystone correction are in use.
  * Fixed RandR per-CRTC gamma persistence across modeswitches and
    VT-switches.
  * Fixed a bug that caused the X server to sometimes hang in response to
    input events.
  * Fixed a reduction in rendering performance for core X11 rendering on
    certain GPUs that occurred in the 290.* series of releases.
  * Fixed a bug that prevented PowerMizer from working correctly on
    some boards with GDDR5 memory, such as some GeForce GT 240 SKUs.
  * Added support for the following GPUs:
  * GeForce GTX 660
  * GeForce GTX 650
  * Fixed a bug that caused OpenGL applications to not animate properly
    when a rotation or a transformation was applied on some older X
    server versions.
  * Enabled FXAA with Unified Back Buffers.
  * Fixed a bug that prevented the "Reset Hardware Defaults" button in
    the Display Settings page of nvidia-settings from being activated.
* Thu Aug 30 2012 sndirsch@suse.com
- always let x11-video-nvidiaG02 require the correct version of
  nvidia-gfxG02-kmp, since via the preamble file we do the
  provides now version-wise
* Thu Aug 30 2012 sndirsch@suse.com
- let x11-video-nvidiaG02/nvidia-computeG02 require the correct
  version of nvidia-gfxG02-kmp on openSUSE > 12.2 (new feature in
  kernel-devel introduced after openSUSE 12.2 release)
* Wed Aug 29 2012 sndirsch@suse.com
- update to driver release 304.43
  * Added support for the GeForce GTX 660 Ti, Quadro K5000,
    Quadro K5000M, Quadro K4000M, Quadro K3000M, NVS 510
  * Fixed a bug that caused pre-release versions of X.Org xserver
    1.13 to crash when certain GLX operations were performed,
    such as when starting Firefox.
  * Fixed a bug that caused VDPAU to hang when expanding the
    YouTube Flash Player.
  * Fixed a bug that caused gnome-settings-daemon to revert
    display configuration changes made by nvidia-settings.
  * Updated nvidia-settings to use RandR per-CRTC gamma control,
    when available. When controlling an X server with support for
    RandR 1.2, nvidia-settings will display the color correction
    widget as a tab within each display device page, instead of a
    per-X screen color correction page.
  * Fixed a bug that prevented the display palette from being
    updated immediately after an application called XStoreColors.
  * Added the ability to select and move X screens in the
    "X Server Display Configuration" page of nvidia-settings via
    Ctrl-(Left)Click + Drag.
* Tue Aug 14 2012 sndirsch@suse.com
-  304.37 has become certified
* Fri Aug 10 2012 sndirsch@suse.com
- update to beta driver 304.37
  * Removed the ability to enable SLI on GPUs with ECC enabled.
  * Fixed several bugs that prevented some RandR transform geometries from
    being applied.
  * Fixed a bug that caused frequent hangs or crashes on some systems.
  * Fixed a bug that would cause corruption and performance issues in certain
    OpenGL applications such as Amnesia: The Dark Descent on GeForce 6 and 7
    GPUs.
* Tue Aug  7 2012 sndirsch@suse.com
- update to beta driver 304.32, which includes the following
  change:
  * Implemented hotfix for a privilege escalation vulnerability
    reported on August 1, 2012.  For more details, see:
    http://nvidia.custhelp.com/app/answers/detail/a_id/3140
* Wed Jun 27 2012 sndirsch@suse.com
- update to beta driver 302.17; Release highlights since 302.11
  * Made nvidiaXineramaInfoOrder consistent with the RRSetOutputPrimary and
    RRGetOutputPrimary RandR requests: changes to either
    nvidiaXineramaInfoOrder or RandR OutputPrimary will be reflected in the
    other.
  * Fixed an interaction problem between RandR 1.2, ConstrainCursor, and
    panning that prevented panning from working properly.
  * Fixed a bug that caused RandR RRNotify_CrtcChange events to not be
    generated when switching between MetaModes with the same total size but
    different layout of display devices.  This bug caused some window managers
    to not update their layouts in response to switching same-sized MetaModes.
  * Added support for desktop panning when rotation, reflection, or
    transformation is applied to a display device (either through RandR or
    through the MetaMode syntax); panning would previously be ignored in that
    case.
  * Added an "EDID" property to RandR 1.2 outputs.  This property contains the
    binary contents of the connected monitor's extended display identification
    data, which allows applications such as the GNOME display properties
    dialog to query information about it.
  * Fixed a bug that caused audio over HDMI to not work on some GPUs after
    querying the RandR configuration (e.g., `xrandr -q`).
  * Added the "nvidiaXineramaInfo" X configuration option to report the layout
    of multiple display devices within an X screen.  This is enabled by
    default.  When disabled on X servers with RandR 1.2 support, the NVIDIA X
    driver will report one screen-sized region.  When disabled on X servers
    without RandR 1.2 support, no Xinerama information will be reported.  For
    backwards compatibility, the "NoTwinViewXineramaInfo" option disables
    nvidiaXineramaInfo.
  * Added the "nvidiaXineramaInfoOrder" X configuration option as a
    replacement for "TwinViewXineramaInfoOrder".  For backwards compatibility,
    "TwinViewXineramaInfoOrder" is kept as a synonym for
    "nvidiaXineramaInfoOrder".
  * Added the "nvidiaXineramaInfoOverride" X configuration option as a
    replacement for "TwinViewXineramaInfoOverride".  For backwards
    compatibility, "TwinViewXineramaInfoOverride" is kept as a synonym for
    "nvidiaXineramaInfoOverride".
  * Fixed a bug that prevented the use of some SLI Mosaic topologies.
  * Added the "MetaModeOrientation" X configuration option as a replacement
    for "TwinViewOrientation".  "TwinViewOrientation" is kept as a synonym for
    "MetaModeOrientation", for backwards compatibility.
  * Disabled the use of certain OpenGL optimizations with Autodesk Maya and
    Mudbox, due to conflicts between these applications and the
    optimizations. Some performance loss in Autodesk Maya and Mudbox is
    possible, as a result.
  * Added support for the following GPUs:
  * GeForce GT 620M
  * GeForce GT 640M
  * GeForce GT 640M LE
  * GeForce GT 650M
  * GeForce GTX 660M
  * GeForce GTX 670M
  * GeForce GTX 675M
  * GeForce GTX 555
  * GeForce GTX 560 SE
  * GeForce GT 415
  * GeForce GTX 460 v2
  * NVS 5400M
  * NVS 310
  * Quadro 410
  * Fixed a behavior issue where redundant DPMS state transitions were leading
    to unexpected screen blanking on DisplayPort displays.
* Mon Jun 11 2012 sndirsch@suse.com
- update to beta driver 302.11; Release highlights since 302.07:
  * Added support for the following GPUs:
    GeForce GTX 690
    GeForce GTX 670
    GeForce 605
    GeForce GT 610
    GeForce GT 630
    GeForce GT 640
    GeForce GT 645
  * Fixed a bug affecting some G-Sync configurations which could
    cause active stereo content to be inverted on some display
    devices.
  * Added support for calculating the physical size and DPI of
    each RandR 1.2 Output using the EDID Detailed Timing
    Description.
  * Fixed a bug that prevented a workaround for the invalid EDID
    in certain AUO laptop flat panels from being applied, leading
    to an 800x600 desktop repeated several times across the screen.
  * Fixed a bug that caused the link configuration of DisplayPort
    devices to be reported incorrectly in nvidia-settings.
* Tue May 15 2012 sndirsch@suse.com
- update to beta driver 302.07 with RANDR 1.2 support
* Fri May 11 2012 sndirsch@suse.com
- update to 295.49
  * Added support for the following GPU: GeForce GTX 690
  * Fixed a problem where starting, stopping, and moving OpenGL
    application windows was very slow on Quadro FX 4600,
    Quadro FX 5600, GeForce 8800 GTX, GeForce 8800 GTS, and
    GeForce 8800 Ultra.
  * Fixed an OpenGL performance regression which affected
    Geforce 6 and Geforce 7 series integrated GPUs.
* Fri Apr 13 2012 sndirsch@suse.com
- update to 295.40
  * Closed a security vulnerability which made it possible for
    attackers to reconfigure GPUs to gain access to arbitrary
    system memory. For further details, see:
    http://nvidia.custhelp.com/app/answers/detail/a_id/3109
  * Fixed a bug that caused DisplayPort devices to occasionally
    fail to turn back on after the system is resumed from suspend.
  * Added a ModeValidation X configuration option token,
    "AllowNon3DVisionModes", to allow modes that are not optimized
    for NVIDIA 3D Vision to be validated on 3D Vision monitors.
  * Added support for the following GPUs:
  * GeForce GT 635M
  * GeForce 610M
* Fri Mar  2 2012 sndirsch@suse.com
- update to 295.20
  * Fixed a bug that caused black areas to appear on the back faces of
    some models in Maya.
  * Fixed a bug that resulted in the printing of spurious loader error
    messages.
  * Fixed a bug that could cause X to crash after hotplugging displays.
  * Fixed a bug which caused face selections to be misrendered in
    Maya when using the paint selection tool.
  * Improved performance for interactive tools in Mudbox.
  * Added a "--no-opengl-files" option to nvidia-installer to allow
    installation of the driver without OpenGL files that might conflict
    with already installed OpenGL implementations.
  * Split the DFP configuration page in nvidia-settings into multiple
    tabs, allowing the controls to be displayed on smaller screens.
  * Fixed a bug that could cause some OpenGL applications (including
    desktop environments like KDE and GNOME Shell) to hang.
  * Fixed a bug that prevented the internal panel from working on some
    laptops with GeForce 7 series GPUs.
  * Fixed an OpenGL bug where using display lists on Fermi-based GPUs
    could result in missing rendering in some cases.
  * Fixed an OpenGL bug that caused incorrect rendering when using
    framebuffer objects to render to 16-bit color textures with
    alpha.
  * Added support for the following GPU: Tesla X2090
  * Fixed two bugs that caused sporadic application crashes in some multi-
    threaded OpenGL applications.
  * Fixed a bug that caused creating OpenGL 4.2 contexts
    with glXCreateContextAttribsARB to fail.
  * Fixed a bug that caused OpenGL to print
    Xlib:  extension "NV-GLX" missing on display ":0".
    when used with a non-NVIDIA implementation of the GLX X extension.
  * Implemented color depth 30 (10 bits per component) support for GeForce 8
    series and higher GPUs.
  * Implemented support for constraining cursors to the visible regions of
    connected displays; see the "ConstrainCursor" X Option in the README for
    details.
  * Added support for the following GPU: NVS 5200M
  * Added support for deleting SDI audio ancillary data packets when a video
    frame is dropped on a Quadro SDI Output device.  See the
    NV_CTRL_GVO_ANC_BLANKING attribute in NVCtrl.h for details.  This option
    can be set via the "GvoAudioBlanking" attribute in nvidia-settings.
  * Added support for xserver 1.11.99.901 (also known as 1.12 RC1).
  * Fixed a bug that would cause Firefox to abort on pages with Flash when
    layers acceleration was force-enabled on Linux and Solaris.
* Thu Mar  1 2012 sndirsch@suse.com
- split off generic vdpau libs/headers instead of
  providing/obsoleting these (bnc#749681)
* Thu Dec  8 2011 sndirsch@suse.com
- moved libnvidia-ml to nvidia-computeG02 subpackage
* Tue Dec  6 2011 sndirsch@suse.com
- provide/obsolete libvdpau1, libvdpau-devel, libvdpau_trace1 on
  suse < 11.3, since these packages have been introduced with SP2
  and there is no way to distinguish SP1 and SP2 in a specfile.
  Also added vpdauinfo tool to better fullfill the requirements for
  these provides. (bnc #734789)
* Thu Nov 24 2011 sndirsch@suse.com
- update to 290.10
  * adds support for GeForce GTX 460 SE v2 and GeForce 510
  * bugfixes; among these is the following
  - Fixed a regression that caused blank/white windows when
    exhausting video memory on GeForce 6 and 7 series GPUs
    while using composited desktops.
* Thu Nov  3 2011 sndirsch@suse.com
- libnvidia-ml.so.1 needs to be in main package since required by
  nvidia-debugdump
* Wed Oct  5 2011 prusnak@opensuse.org
- update to 285.05.09
  * Added support for the following GPU:
    GeForce GT 520MX
  * Fixed a bug causing a Linux kernel BUG when retrieving
    CPU information on some systems.
  * Fixed a bug causing some applications to hang on exit.
  * Fixed a bug causing flickering in some GPU/display combinations.
  * Fixed a bug that could result in poor OpenGL performance after
    hotplugging a monitor.
  * Fixed a bug causing possible text corruption when recovering
    from GPU errors.
  * Fixed a bug causing corruption of images which are 2047 pixels wide.
  * Improved performance of the RENDER extension on Fermi-based GPUs.
  * Fixed a bug causing the X server to crash after a VT-switch while
    running an OpenGL stereo application which is a member of a swap group.
* Tue Oct  4 2011 sndirsch@suse.com
- no longer generate sax2/hwinfo metafiles and try to run sax2 on
  openSUSE > 11.2, which has been dropped with openSUSE 11.3
  (bnc #721867)
* Thu Sep 22 2011 sndirsch@suse.com
- Add 'Provides: nvidia_driver' and 'Conflicts: fglrx_driver' to
  avoid both drivers being installed at the same time (bnc #718209)
* Mon Sep 19 2011 sndirsch@suse.com
- added new pci ids also to .new file
* Sat Sep 17 2011 dmacvicar@suse.de
- rename /etc/ld.so.conf.d/nvidia-gfxG02 to
  /etc/ld.so.conf.d/nvidia-gfxG02.conf as Factory ld.so.conf
  includes /etc/ld.so.conf.d/*.conf only (bnc#718734)
* Wed Sep 14 2011 dmacvicar@suse.de
- update to 280.13
  * Added support for the following GPUs:
    GeForce GTX 570M
    GeForce GTX 580M
  * Fixed a GLX bug that could cause the X server to crash when
    rendering a display list using GLX indirect rendering.
  * Fixed a GLX bug that could cause a hang in applications that use
    X server grabs.
  * Fixed an X driver bug that caused 16x8 stipple patterns to be
    rendered incorrectly.
  * Fixed a GLX_EXT_texture_from_pixmap bug that caused corruption
    when texturing from sufficiently small pixmaps and, in particular,
    corruption in the GNOME Shell Message Tray.
  * Added unofficial GLX protocol support (i.e., for GLX indirect
    rendering) for the following OpenGL extension:
    GL_EXT_vertex_attrib_64bit
  * Added GLX protocol support (i.e., for GLX indirect rendering) for
    the following OpenGL extensions:
    GL_ARB_half_float_pixel
    GL_EXT_packed_depth_stencil
* Thu Aug  4 2011 sndirsch@novell.com
- update to 275.21
  * Restored the release splash screen in the NVIDIA X driver (the
    beta splash screen was accidentally reenabled between 275.09.07
    and 275.19).
  * Fixed a bug that caused nvidia-settings to crash when
    configuring multiple X screens after all monitors were
    unplugged from one of the X screens.
  * Fixed a bug in nvidia-settings that caused the display
    configuration page to show extra disabled displays after
    connecting a new monitor.
  * Added X configuration options "3DVisionProHwButtonPairing",
    "3DVisionProHwSinglePairingTimeout",
    "3DVisionProHwMultiPairingTimeout", and
    "3DVisionProHwDoubleClickThreshold" to configure hardware
    button based pairing in NVIDIA 3D Vision Pro. See "Appendix B.
    X Config Options" in the README for more information.
  * Fixed a bug that prevented initialization of the NVIDIA 3D
    Vision or NVIDIA 3D Vision Pro hub if no EDID was present.
* Mon Jul  4 2011 sndirsch@novell.com
- Add /etc/ld.so.conf.d/nvidia-gfxG02 for ldconfig (bnc #671725)
* Sun Jul  3 2011 ro@suse.de
- update to 275.09.07
  * Fixed a bug that caused desktop corruption in GNOME 3 after a
    VT-switch or suspend/resume cycle.
  * Added support for the following GPUs:
  * GeForce GTX 560 * GeForce GT 545 * GeForce GTX 560M * GeForce 410M
  * GeForce 320M * GeForce 315M
  * Quadro 5010M * Quadro 3000M * Quadro 4000M
  * Fixed a bug that caused freezes and crashes when resizing windows in
    KDE 4 with desktop effects enabled using X.Org X server version 1.10
    or later.
  * Modified the X driver to request that hardware inform the audio driver
    whenever a display is disabled. This will allow the audio driver to
    generate the appropriate jack unplug events to applications.
  * Added support for the GL_EXT_x11_sync_object extension.  See the
    extension specification in the OpenGL registry here:
    http://www.opengl.org/registry/specs/EXT/x11_sync_object.txt
    for more details.
  * Improved performance of window resize operations in KDE 4 on systems
    with slow CPUs.
  * Added support for hardware button based pairing to NVIDIA 3D Vision Pro.
    Single click button on the hub to enter into a pairing mode which pairs
    one pair of glasses at a time. Double click the same button on the
    hub to enter into a pairing mode which pairs multiple pairs of glasses
    at a time.
  * Added unofficial GLX protocol support (i.e., for GLX indirect
    rendering) for the following OpenGL extensions:
    GL_NV_framebuffer_multisample_coverage
    GL_NV_texture_barrier
  * Added GLX protocol support (i.e., for GLX
    indirect rendering) for the following OpenGL extension:
    GL_NV_register_combiners2
  * Fixed a bug that caused the pop-out and external DVI displays to go blank
    on Lenovo ThinkPad W701 laptops.
  * Fixed a bug that caused corruption on the menus in OpenOffice.org when the
    screen is rotated.
  * Improved performance of certain memory allocations.
  * Fixed a bug that caused Java2D widgets to disappear when Java is
    configured to render using FBOs.
  * Fixed a bug that caused nvidia-settings to crash while saving the X
    configuration file on some Linux distributions.
  * Added a new X configuration option "BaseMosaic" which can be used to
    extend a single X screen transparently across all of the available
    display outputs on each GPU. See "Appendix B. X Config Options" in the
    README for more information.
- release 270 changes
  * Fixed a bug causing incorrect reporting of GPU core and ambient
    temperatures via NV-CONTROL.
  * Fixed a bug in the VDPAU presentation queue that could cause 1
    second hangs when transitioning from blit-based display to overlay-
    based display. This would most commonly happen when disabling a
    compositing manager.
  * Fixed a bug that could cause crashes when capturing SDI video.
  * Fixed a corner-case in which the OpenGL driver could leak resources
    in applications utilizing fork().
  * Addressed a Linux kernel interface compatibility problem that could
    lead to ioremap() errors and, potentially, functional and/or
    stability problems.
  * Fixed a bug that caused SLI initialization to fail on some Intel
    based systems.
  * Fixed a bug that caused SLI initialization to fail when using recent
    Linux kernels, such as 2.6.38.
* Wed Apr 27 2011 sndirsch@novell.com
- update to 270.30
  * Added support for GeForce GTX 560 Ti
  * Added new shared library: libnvidia-ml.so.
    NVML provides programmatic access to static information and
    monitoring data for NVIDIA GPUs, as well as limited managment
    capabilities. It is intended for use with Tesla compute products.
* Tue Apr  5 2011 bwiedemann@novell.com
- Added nvidia-computeG02 subpackage
- Have kmp only recommend x11-video-nvidiaG02 instead of require
* Mon Mar 21 2011 sndirsch@novell.com
- update to 260.19.44
  * Updated the NVIDIA X driver to not update mode timings for
    G-Sync compatibility when NVIDIA 3D Vision or NVIDIA 3D
    VisionPro is enabled along with a G-Sync device.
  * Added support for Quadro 2000 D, Quadro 400
* Sat Feb  5 2011 sndirsch@novell.com
- update to 260.19.36
  * Updated the NVIDIA kernel module to ensure that all system
    memory allocated by it for use with GPUs or within user-space
    components of the NVIDIA driver stack is initialized to zero.
    A new NVIDIA kernel module option,
    InitializeSystemMemoryAllocations, allows administrators to
    revert to the previous behavior.
  * Fixed a bug that caused X servers version 1.9 and higher to
    crash when color index overlays were enabled.
  * Fixed a bug that caused pixel value 255 to be treated as
    transparent in color index overlays.
* Wed Dec 22 2010 sndirsch@novell.com
- update to 260.19.29
  * Added support for the following GPUs:
  * GeForce GTX 460 SE
  * GeForce GTX 570
  * Quadro 5000M
  * NVS 300
  * Fixed a bug that caused some OpenGL applications to become
    unresponsive for up to a minute on some GPUs when changing
    the resolution or refresh rate.
  * Added support for NVIDIA 3D Vision Pro.
    See the "Stereo" X configuration documentation in the README
    for further details.
  * Added a new X configuration option "3DVisionProConfigFile"
    to allow user provide a filename which NVIDIA X driver uses
    to store 3D Vision Pro configuration settings.
    See "Appendix B. X Config Options" in the README for
    more information.
* Thu Nov 18 2010 sndirsch@novell.com
- update to 260.19.21
  * Fixed a race condition in OpenGL that could cause crashes with
    multithreaded applications.
  * Fixed a bug that may cause OpenGL applications which fork to
    crash.
  * Fixed a bug in VDPAU that caused it to attempt allocation of
    huge blocks of system memory. This regression was introduced
    in the 260.* driver series.
* Fri Oct 15 2010 sndirsch@novell.com
-  update to 260.19.12
  * adds libnvcuvid
  * removes header files for OpenGL, VDPAU, CUDA and OpenCL
* Wed Sep  8 2010 sndirsch@suse.de
- added .so symlinks for libOpenCL/libcuda
* Fri Sep  3 2010 sndirsch@suse.de
- added missing cl.h and libOpenCL.so*
* Tue Aug 31 2010 sndirsch@suse.de
- update to 256.53
* Tue Aug 31 2010 sndirsch@suse.de
- update to 256.52
  * Fixed a bug that prevented XvMC from initializing in most
    cases.
  * Added support for xorg-server video driver ABI version 8,
    which will be included in the upcoming xorg-server-1.9
    series of releases.
  * Fixed a bug that caused extremely slow rendering of OpenGL
    applications on X screens other than screen 0 when using a
    compositing manager.
  * Fixed a regression introduced after 256.35 that caused
    stability problems on GPUs such as GeForce GT 240.
  * Fixed a slow kernel virtual address space leak observed when
    starting and stopping OpenGL, CUDA, or VDPAU applications.
  * Fixed a bug that left the system susceptible to hangs when
* Mon Aug  9 2010 sndirsch@suse.de
- update to 256.44
  * Added Support for Quadro 4000, Quadro 5000, and Quadro 6000.
  * Updated nvidia-installer to detect the nouveau kernel module
    and fail with an appropriate error message.
  * Added information to the NVIDIA driver README on how to
    disable the nouveau driver.
  * Fixed VDPAU to not print a debug error message when calling
    VdpVideoMixerQueryFeatureSupport with an unsupported or
    unknown VdpVideoMixerFeature.
  * Removed the requirement that in TwinView passive stereo,
    MetaModes must have identical viewports on each monitor.
  * Removed the requirement that in active stereo, all monitors
    must use identical modetimings.
  * Enhanced VDPAU to better report certain kinds of initialization
    error.
  * Fixed a regression that caused Xv to return BadAlloc errors on
    AGP systems when using the AGP GART driver contained in the
    NVIDIA driver. This fixes the problem reported in nvnews.net
    thread 151199.
* Mon Jul 26 2010 sndirsch@suse.de
- tls/libnvidia-tls.so.* instead of libnvidia-tls.so.* needs to be
  copied to usr/%%_lib/tls; otherwise a libglx.so segfaults
  immediately during Xserver start
* Wed Jul 21 2010 sndirsch@suse.de
- update to 256.35
  * specfile adjustments done by Vitaliy Tomin; thanks a lot!
* Sat Jun 12 2010 sndirsch@suse.de
- update to 195.36.31
  * Fixed a problem with SLI SFR, AFR, and SLIAA modes with GeForce
    GTX 480 and GeForce GTX 470 and high-resolution display modes.
* Sun May  2 2010 sndirsch@suse.de
- fixed build of libvdpau on sle10
* Sat Apr 24 2010 sndirsch@suse.de
- adjusted Requires for VDPAU packages, which have been renamed
  and splitted meanwhile
* Sat Apr 24 2010 sndirsch@suse.de
- update to 195.36.24
  * Added support for the following GPUs:
    . GeForce GTX 480
    . GeForce GTX 470
    . Tesla C2050
  * Fixed a problem that caused occasional red flashes in XVideo
    frames.
  * Added official support for xserver 1.8.  The -ignoreABI option
    is no longer required with this version of the server.
  * Updated the "Supported NVIDIA GPU Products" list to include
    various supported GPUs that were missing previously.
* Thu Apr 22 2010 sndirsch@suse.de
- use libvdpau sources for creating libvdpau,libvdpau_trace on
  openSUSE < 11.3; in the long run NVIDIA is no longer going to
  ship these anyway (bnc #596481)
* Wed Apr 21 2010 sndirsch@suse.de
- on openSUSE >= 11.3 only install libvdpau_nvidia and require
  packages libvdpau,libvdpau-devel (which include libvdpau,
  libvdpau_trace) (bnc #596481)
* Wed Apr 21 2010 sndirsch@suse.de
- moved libvdpau_nvidia/libvdpau_trace to /usr/lib/vdpau;
  created comp. symlinks libvdpau_nvidia.so/libvdpau_trace.so
  (bnc #596481)
* Mon Mar 29 2010 sndirsch@suse.de
- recreate initrd without KMS, if the use of KMS is enabled in
  initrd
* Thu Mar 18 2010 sndirsch@suse.de
- update to 195.36.15
- obsoletes conftest.sh.diff-2.6.33,
  nvacpi-acpi_walk_namespace-2.6.33
- new: /etc/OpenCL/vendors/, /usr/include/CL
- added 0x0a2c/0x0a7c as supported (missing in documentation)
* Fri Dec 18 2009 sndirsch@suse.de
- update to 190.53
* Fri Oct 30 2009 sndirsch@suse.de
- update to 190.42
* Sat Aug 22 2009 sndirsch@suse.de
- update to 185.18.36
  * Fixed a bug that caused kernel panics when starting X on some
    mobile GPUs.
  * fixed various VDPAU issues
* Fri Aug  7 2009 ro@suse.de
- update to 185.18.31
* Thu Jun 25 2009 sndirsch@suse.de
- added .so symlink for vdpau lib (bnc #516268)
- added 32bit cuda/vdpau libs
* Sat Jun  6 2009 sndirsch@suse.de
- release 185.14.18
  * removed support for GeForce 6800, GeForce 6800 LE,
    GeForce 6800 GT, GeForce 6800 XT (0x0211, 0x0212, 0x0215, 0x0218)
  * added support for GeForce 9300 / nForce 730i (0x086C)
  * various fixes
* Tue Apr 28 2009 sndirsch@suse.de
- release 180.51
  * Added support for the following GPUs:
  - GeForce 9600 GSO 512
  - GeForce 9400 GT
  - GeForce GTS 250
  - GeForce GT 140
  - GeForce GT 130
  * various fixes
* Mon Mar 30 2009 sndirsch@suse.de
- release 180.44
  * Next to a good number of other bugfixes,
    http://www.nvidia.com/object/linux_display_ia32_180.44.html
    lists "Fixed OpenGL crashes while running KDE4's Plasma".
* Sat Mar  7 2009 sndirsch@suse.de
- back to stable release 180.29
* Wed Feb 25 2009 sndirsch@suse.de
- release 180.35
  * Added support for GeForce GT 120, GeForce G100, Quadro FX 3700M
  * Fixed a bug that caused Maya to freeze when overlays are
    enabled.
  * Added support for RG renderbuffers in OpenGL 3.0.
  * Added support for OpenGL 3.0 floating-point depth buffers.
  * Fixed a problem that caused Valgrind to crash when tracing a
    program that uses OpenGL.
  * various VDPAU updates
* Mon Feb 16 2009 sndirsch@suse.de
- Xwrapper:
  * /var/X11R6/bin no longer covered by FHS; switched to
    /var/lib/X11 (bnc #470969)
* Wed Feb 11 2009 sndirsch@suse.de
- release 180.29
  * Added support for GeForce GTX 285/295, GeForce 9300 GE,
    Quadro NVS 420
  * Added support for OpenGL 3.0 for GeForce 8 series and newer
    GPUs.
  * various bugfixes related to VDPAU
  * Improved workstation OpenGL performance.
  * Fixed an X driver acceleration bug that resulted in Xid errors
    on GeForce 6 and 7 series GPUs.
  * Updated the X driver to consider GPUs it does not recognize
    supported, allowing it to drive some GPUs it previously ignored.
  * Added the ability to run distribution provided pre- and post-
    installation hooks to 'nvidia-installer'; please see the
    'nvidia-installer' manual page for details.
  * Updated the X driver's metamode parser to allow mode names with
    periods (i.e. '.'s).
  * Fixed an X driver performance problem on integrated GPUs.
  * Fixed a stability problem with OpenGL applications using FSAA.
  * Fixed an initialization problem that caused some AGP GPUs to be
    used in PCI compatibility mode.
  * Fixed a bug that could result in stability problems after
    changing clock settings via the Coolbits interface.
  * Fixed a problem with hotkey switching on some recent mobile GPUs.
  * Worked around a power management regression in and improved
    compatibility with recent Linux 2.6 kernels.
* Thu Feb  5 2009 sndirsch@suse.de
- make rpmlint happy on head/factory
* Fri Jan  9 2009 sndirsch@suse.de
- release 180.22
  * Added support for the following GPUs:
  - Quadro FX 2700M
  - GeForce 9400M G
  - GeForce 9400M
  - GeForce 9800 GT
  - GeForce 8200M G
  - GeForce Go 7700
  - GeForce 9800M GTX
  - GeForce 9800M GT
  - GeForce 9800M GS
  - GeForce 9500 GT
  - GeForce 9700M GT
  - GeForce 9650M GT
  - GeForce 9500 GT
  * Added initial support for PureVideo-like features via the new
    VDPAU API (see the vdpau.h header file installed with the driver).
  * Added support for CUDA 2.1.
  * Added preliminary support for OpenGL 3.0.
  * Added new OpenGL workstation performance optimizations.
  * Enabled the glyph cache by default and extended its support to all
    supported GPUs.
  * Disabled shared memory X pixmaps by default; see the
    "AllowSHMPixmaps" option.
  * Improved X pixmap placement on GeForce 8 series and later GPUs.
  * Improved stability on some GeForce 8 series and newer GPUs.
  * Fixed a regression that could result in window decoration
    corruption when running Compiz using Geforce 6 and 7 series GPUs.
  * Fixed an nvidia-settings crash when xorg.conf contains Device and
    Screen sections but no ServerLayout section.
  * Fixed a problem parsing the monitor sync range X config file
    options.
  * Fixed a problem with the SDI sync skew controls in
    nvidia-settings.
  * Fixed a problem that caused some SDI applications to hang or
    crash.
  * Added support for SDI full-range color.
  * Improved compatibility with recent Linux kernels.
- fixes bnc #429010
* Thu Nov 13 2008 sndirsch@suse.de
- release 177.82
  * Added support for the following new GPUs:
  - Quadro NVS 450
  - Quadro FX 370 LP
  - Quadro FX 5800
  - Quadro FX 4800
  - Quadro FX 470
  - Quadro CX
  * Fixed a problem on recent mobile GPUs that caused a power
    management resume from S3 to take 30+ seconds.
  * Fixed a problem with hotkey switching on some recent mobile
    GPUs.
  * Fixed an image corruption issue seen in FireFox 3.
* Fri Oct 17 2008 olh@suse.de
- add ExclusiveArch x86 x86_64
* Tue Oct  7 2008 sndirsch@suse.de
- - release 177.80
  * Added support for GeForce 9500 GT
  * Fixed a regression that caused the 'Auto' SLI X option
    setting to not enable SLI.
  * Fixed a bug that caused system hangs when using the NV-CONTROL
    interface to change GPU clock frequencies.
  * Updated mode validation, in cases when no EDID is detected,
    such that 1024x768 @ 60Hz and 800x600 @ 60Hz are
    allowed, rather than just 640x480 @ 60Hz.
  * Fixed corruption when using SLI in SFR mode with
    OpenGL-based composite managers.
  * Added a workaround for broken EDIDs provided by some Acer
    AL1512 monitors.
  * Updated the X driver to consider /sys/class/power_supply
    when determining the AC power state.
* Wed Sep 24 2008 sndirsch@suse.de
- release 177.76
  * Added support for the following new GPUs: GeForce 9500 GT
  * Fixed a bug that caused GPU errors when applications used the X
    RENDER extension's repeating modes in conjunction with
    color-index overlays or rotation on GeForce 7 series and older
    GPUs.
  * Fixed a bug that caused system hangs when using the NV-CONTROL
    interface to change GPU clock frequencies.
  * Fixed a text rendering performance regression on GeForce 7
    series and older GPUs when InitialPixmapPlacement is set to 2.
  * Updated mode validation, in cases when no EDID is detected,
    such that 1024x768 @ 60Hz and 800x600 @ 60Hz are allowed,
    rather than just 640x480 @ 60Hz.
  * Improved power management support.
  * Improved compatibility with recent Linux 2.6 kernels.
  * Fixed a regression that caused the 'Auto' SLI X option setting
    to not enable SLI.
  * Added a workaround for broken EDIDs provided by some Acer
    AL1512 monitors.
* Sun Aug 31 2008 sndirsch@suse.de
- created package
