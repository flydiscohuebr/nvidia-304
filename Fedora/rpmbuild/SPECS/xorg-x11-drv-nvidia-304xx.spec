%global        _nvidia_serie       nvidia-304xx
%global        _nvidia_libdir      %{_libdir}/%{_nvidia_serie}
%global        _nvidia_xorgdir     %{_nvidia_libdir}/xorg

%global	       debug_package %{nil}
%global	       __strip /bin/true

Name:            xorg-x11-drv-nvidia-304xx
Version:         304.137
Release:         2%{?dist}
Summary:         NVIDIA's 304xx serie proprietary display driver for NVIDIA graphic cards

Group:           User Interface/X Hardware Support
License:         Redistributable, no modification permitted
URL:             http://www.nvidia.com/
Source0:         https://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}.run
Source1:         https://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source2:         99-nvidia.conf
Source3:         nvidia-xorg.conf
Source5:         00-avoid-glamor.conf
Source6:         blacklist-nouveau.conf

BuildRoot:       %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:   desktop-file-utils
%if 0%{?fedora} > 11 || 0%{?rhel} > 5
ExclusiveArch: i686 x86_64
%else 0%{?fedora} == 11
ExclusiveArch: i586 x86_64
%endif
#Obsoletes:  nvidia-xconfig < 1.0-30
#Provides:  nvidia-xconfig = %{version}-%{release}
#Obsoletes:  nvidia-settings < 1.0-34
#Provides:  nvidia-settings = %{version}-%{release}
#Obsoletes:  nvidia-settings-desktop < 1.0-34
#Provides:  nvidia-settings-desktop = %{version}-%{release}

Requires:        which
Requires:        %{_nvidia_serie}-kmod >= %{version}
%if 0%{?fedora} > 10 || 0%{?rhel} > 5
Requires:        %{name}-libs%{_isa} = %{version}-%{release}
%else
Requires:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
%endif

Requires(post):  ldconfig
Requires(postun):  ldconfig

#Introduced in F17 when 304xx was splitted
Obsoletes:       xorg-x11-drv-nvidia < 1:%{version}-1000
Provides:        xorg-x11-drv-nvidia = 1:%{version}-1001
Obsoletes:       nvidia-kmod < 1:%{version}-1000
Obsoletes:       nvidia-kmod-common < 1:%{version}-1000
Provides:        nvidia-kmod-common = 1:%{version}-1001

Obsoletes:       %{_nvidia_serie}-kmod < %{version}
Provides:        %{_nvidia_serie}-kmod-common = %{version}
Conflicts:       xorg-x11-drv-nvidia-latest
Conflicts:       xorg-x11-drv-nvidia-beta
Conflicts:       xorg-x11-drv-nvidia-96xx
Conflicts:       xorg-x11-drv-nvidia-173xx
Conflicts:       xorg-x11-drv-catalyst
Conflicts:       xorg-x11-drv-catalyst-legacy


#Support for cuda
#Don't put an epoch here
Provides:        cuda-driver = %{version}

%{?filter_setup:
%filter_from_provides /^libnvidia/d;
%filter_from_provides /^libGLcore\.so/d;
%filter_from_provides /^libGL\.so/d;
%filter_from_provides /^libvdpau_nvidia\.so\.1/d;
%filter_from_provides /^libXvMCNVIDIA_dynamic\.so\.1/d;
%filter_from_provides /^libglx\.so/d;
%filter_from_requires /^libnvidia/d;
%filter_from_requires /^libGLcore\.so/d;
%filter_from_requires /^libGL\.so/d;
%filter_from_requires /^libvdpau_nvidia\.so\.1/d;
%filter_from_requires /^libXvMCNVIDIA_dynamic\.so\.1/d;
%filter_from_requires /^libglx\.so/d;
%filter_setup
}

%description
This package provides the most recent NVIDIA display driver which allows for
hardware accelerated rendering with NVIDIA chipsets GeForce6/7 series.
GeForce5 and below are NOT supported by this release.

For the full product support list, please consult the release notes
for driver version %{version}.

Please use the following documentation:
http://rpmfusion.org/Howto/nVidia


%package devel
Summary:         Development files for %{name}
Group:           Development/Libraries
%if 0%{?fedora} > 10 || 0%{?rhel} > 5
Requires:        %{name}-libs%{_isa} = %{version}-%{release}
%else
Requires:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
%endif
#Introduced in F17 when 304xx was splitted
Obsoletes:       xorg-x11-drv-nvidia-devel < 1:%{version}-1000
Provides:        xorg-x11-drv-nvidia-devel = 1:%{version}-1001

%description devel
This package provides the development files of the %{name} package,
such as OpenGL headers.

%package libs
Summary:         Libraries for %{name}
Group:           User Interface/X Hardware Support
Requires:        %{name} = %{version}-%{release}
Requires:        libvdpau%{_isa} >= 0.5
Provides:        %{name}-libs-%{_target_cpu} = %{version}-%{release}
#Introduced in F17 when 304xx was splitted
Obsoletes:       xorg-x11-drv-nvidia-libs < 1:%{version}-1000
Provides:        xorg-x11-drv-nvidia-libs = 1:%{version}-1001

%description libs
This package provides the shared libraries for %{name}.


%prep
%setup -q -c -T
sh %{SOURCE0} --extract-only --target nvidiapkg-x86
sh %{SOURCE1} --extract-only --target nvidiapkg-x64
tar -cJf nvidia-kmod-data-%{version}.tar.xz nvidiapkg-*/LICENSE nvidiapkg-*/kernel

%ifarch %{ix86}
ln -s nvidiapkg-x86 nvidiapkg
%else
ln -s nvidiapkg-x64 nvidiapkg
%endif

%build
# Nothing to build
echo "Nothing to build"


%install
rm -rf $RPM_BUILD_ROOT

cd nvidiapkg

# The new 256.x version supplies all the files in a relatively flat structure
# .. so explicitly deal out the files to the correct places
# .. nvidia-installer looks too closely at the current machine, so it's hard
# .. to generate rpm's unless a NVIDIA card is in the machine.

rm -f nvidia-installer*

install -m 0755 -d $RPM_BUILD_ROOT%{_bindir}

# ld.so.conf.d file
install -m 0755 -d       $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/
echo "%{_nvidia_libdir}" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d/%{_nvidia_serie}-%{_lib}.conf

#Blacklist nouveau (since F-11)
install    -m 0755 -d         $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d/
install -p -m 0644 %{SOURCE6} $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d/

# OpenCL config
install    -m 0755         -d $RPM_BUILD_ROOT%{_sysconfdir}/OpenCL/vendors/
install -p -m 0755 nvidia.icd $RPM_BUILD_ROOT%{_sysconfdir}/OpenCL/vendors/

# Simple wildcard install of libs
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_libdir}/tls/
install -m 0755 -d $RPM_BUILD_ROOT%{_libdir}/vdpau/
install -p -m 0755 lib*.so.%{version}          $RPM_BUILD_ROOT%{_nvidia_libdir}/
install -p -m 0755 libOpenCL.so.1.0.0          $RPM_BUILD_ROOT%{_nvidia_libdir}/
install -p -m 0755 tls/lib*.so.%{version}      $RPM_BUILD_ROOT%{_nvidia_libdir}/tls/

#
mkdir -p $RPM_BUILD_ROOT%{_libdir}/xorg/modules/drivers/
mkdir -p $RPM_BUILD_ROOT%{_nvidia_xorgdir}

# .. but some in a different place
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_xorgdir}
install -m 0755 -d $RPM_BUILD_ROOT%{_nvidia_xorgdir}
rm -f $RPM_BUILD_ROOT%{_nvidia_libdir}/lib{nvidia-wfb,glx,vdpau*}.so.%{version}

# Finish up the special case libs
%if 0%{?rhel} == 5
install -p -m 0755 libnvidia-wfb.so.%{version} $RPM_BUILD_ROOT%{_nvidia_xorgdir}
%endif
install -p -m 0755 libglx.so.%{version}        $RPM_BUILD_ROOT%{_nvidia_xorgdir}
install -p -m 0755 nvidia_drv.so               $RPM_BUILD_ROOT%{_libdir}/xorg/modules/drivers/nvidia_drv.so
install -p -m 0755 libvdpau*.so.%{version}     $RPM_BUILD_ROOT%{_libdir}/vdpau/
install -p -m 0644 libXvMCNVIDIA.a             $RPM_BUILD_ROOT%{_nvidia_libdir}/

# Install binaries
install -p -m 0755 nvidia-{bug-report.sh,smi,cuda-proxy-control,cuda-proxy-server,xconfig,settings} \
  $RPM_BUILD_ROOT%{_bindir}

# Install headers
install -m 0755 -d $RPM_BUILD_ROOT%{_includedir}/nvidia/GL/
install -p -m 0644 {gl.h,glext.h,glx.h,glxext.h} $RPM_BUILD_ROOT%{_includedir}/nvidia/GL/

# Install man pages
install    -m 0755 -d   $RPM_BUILD_ROOT%{_mandir}/man1/
install -p -m 0644 *.gz $RPM_BUILD_ROOT%{_mandir}/man1/
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/{nvidia-settings,nvidia-xconfig}*

# Make unversioned links to dynamic libs
for lib in $( find $RPM_BUILD_ROOT%{_libdir} -name lib\*.%{version} ) ; do
  ln -s ${lib##*/} ${lib%.%{version}}
  ln -s ${lib##*/} ${lib%.%{version}}.1
done

# Own the real SONAME for libXvMCNVIDIA
mv $RPM_BUILD_ROOT%{_nvidia_libdir}/libXvMCNVIDIA.so.1 \
   $RPM_BUILD_ROOT%{_nvidia_libdir}/libXvMCNVIDIA_dynamic.so.1

ln -s libOpenCL.so.1.0.0 $RPM_BUILD_ROOT%{_nvidia_libdir}/libOpenCL.so.1
ln -s libOpenCL.so.1.0.0 $RPM_BUILD_ROOT%{_nvidia_libdir}/libOpenCL.so


# Install nvidia icon
mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
install -pm 0644 nvidia-settings.png $RPM_BUILD_ROOT%{_datadir}/pixmaps

# Remove duplicate install
rm $RPM_BUILD_ROOT%{_nvidia_libdir}/libnvidia-{cfg,tls}.so

#Install static driver dependant configuration files
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
install -pm 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
install -pm 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d
sed -i -e 's|@LIBDIR@|%{_libdir}|g' $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
sed -i -e 's|nvidia|%{_nvidia_serie}|g' $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
touch -r %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
install -pm 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/X11/

# Desktop entry for nvidia-settings
desktop-file-install --vendor "" \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications/ \
    --set-icon=nvidia-settings \
    --set-key=Exec --set-value=nvidia-settings \
    nvidia-settings.desktop

#Workaround for self made xorg.conf using a Files section.
ln -fs ../../%{_nvidia_serie}/xorg $RPM_BUILD_ROOT%{_libdir}/xorg/modules/%{_nvidia_serie}-%{version}

#Create the default nvidia config directory
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/nvidia


%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" -eq "1" ]; then
  ISGRUB1=""
  if [[ -f /boot/grub/grub.conf && ! -f /boot/grub2/grub.cfg ]] ; then
      ISGRUB1="--grub"
      GFXPAYLOAD="vga=normal"
  else
      echo "GRUB_GFXPAYLOAD_LINUX=text" >> %{_sysconfdir}/default/grub
      grub2-mkconfig -o /boot/grub2/grub.cfg
  fi
  if [ -x /sbin/grubby ] ; then
    KERNELS=`/sbin/grubby --default-kernel`
    DIST=`rpm -E %%{?dist}`
    ARCH=`uname -m`
    [ -z $KERNELS ] && KERNELS=`ls /boot/vmlinuz-*${DIST}.${ARCH}*`
    for kernel in ${KERNELS} ; do
      /sbin/grubby $ISGRUB1 \
        --update-kernel=${kernel} \
        --args="nouveau.modeset=0 rd.driver.blacklist=nouveau video=vesa:off $GFXPAYLOAD" \
         &>/dev/null
    done
  fi
fi || :


%triggerpostun -- xorg-x11-drv-nvidia < 1:%{version}-1000
if [ "$1" -eq "1" ]; then
  ISGRUB1=""
  if [[ -f /boot/grub/grub.conf && ! -f /boot/grub2/grub.cfg ]] ; then
      ISGRUB1="--grub"
      GFXPAYLOAD="vga=normal"
  else
      echo "GRUB_GFXPAYLOAD_LINUX=text" >> %{_sysconfdir}/default/grub
      grub2-mkconfig -o /boot/grub2/grub.cfg
  fi
  if [ -x /sbin/grubby ] ; then
    KERNELS=`/sbin/grubby --default-kernel`
    DIST=`rpm -E %%{?dist}`
    ARCH=`uname -m`
    [ -z $KERNELS ] && KERNELS=`ls /boot/vmlinuz-*${DIST}.${ARCH}*`
    for kernel in ${KERNELS} ; do
      /sbin/grubby $ISGRUB1 \
        --update-kernel=${kernel} \
        --args="nouveau.modeset=0 rd.driver.blacklist=nouveau video=vesa:off $GFXPAYLOAD" \
         &>/dev/null
    done
  fi
fi || :

%post libs -p /sbin/ldconfig

%posttrans
 [ -f %{_sysconfdir}/X11/xorg.conf.xorg-x11-drv-nvidia_uninstalled ] && \
    mv %{_sysconfdir}/X11/xorg.conf.xorg-x11-drv-nvidia_uninstalled %{_sysconfdir}/X11/xorg.conf
 [ -f %{_sysconfdir}/X11/xorg.conf ] || \
   cp -p %{_sysconfdir}/X11/nvidia-xorg.conf %{_sysconfdir}/X11/xorg.conf || :

%preun
if [ "$1" -eq "0" ]; then
  ISGRUB1=""
  if [[ -f /boot/grub/grub.conf && ! -f /boot/grub2/grub.cfg ]] ; then
      ISGRUB1="--grub"
  fi
  if [ -x /sbin/grubby ] ; then
    DIST=`rpm -E %%{?dist}`
    ARCH=`uname -m`
    KERNELS=`ls /boot/vmlinuz-*${DIST}.${ARCH}*`
    for kernel in ${KERNELS} ; do
      /sbin/grubby $ISGRUB1 \
        --update-kernel=${kernel} \
        --remove-args="nouveau.modeset=0 rdblacklist=nouveau \
            rd.driver.blacklist=nouveau nomodeset video=vesa:off \
            gfxpayload=vga=normal vga=normal" &>/dev/null
    done
  fi
  #Backup and disable previously used xorg.conf
  [ -f %{_sysconfdir}/X11/xorg.conf ] && \
    mv  %{_sysconfdir}/X11/xorg.conf %{_sysconfdir}/X11/xorg.conf.%{name}_uninstalled &>/dev/null
fi ||:

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc nvidiapkg/LICENSE
%doc nvidiapkg/NVIDIA_Changelog
%doc nvidiapkg/README.txt
%doc nvidiapkg/html
%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%config %{_sysconfdir}/OpenCL/vendors/nvidia.icd
%dir %{_sysconfdir}/nvidia
%config %{_sysconfdir}/X11/xorg.conf.d/99-nvidia.conf
%config %{_sysconfdir}/X11/xorg.conf.d/00-avoid-glamor.conf
%config(noreplace) %{_prefix}/lib/modprobe.d/blacklist-nouveau.conf
%config(noreplace) %{_sysconfdir}/X11/nvidia-xorg.conf
%{_bindir}/nvidia-bug-report.sh
%{_bindir}/nvidia-smi
%{_bindir}/nvidia-cuda-proxy-control
%{_bindir}/nvidia-cuda-proxy-server
%{_bindir}/nvidia-settings
%{_bindir}/nvidia-xconfig
# Xorg libs that do not need to be multilib
%dir %{_nvidia_xorgdir}
%{_nvidia_xorgdir}/*.so*
%{_libdir}/xorg/modules/drivers/nvidia_drv.so
%{_libdir}/xorg/modules/%{_nvidia_serie}-%{version}
#/no_multilib
%{_datadir}/applications/*nvidia-settings.desktop
%{_datadir}/pixmaps/*.png
%{_mandir}/man1/nvidia-smi.*
%{_mandir}/man1/nvidia-cuda-proxy-control.1.*

%files libs
%defattr(-,root,root,-)
%dir %{_nvidia_libdir}
%dir %{_nvidia_libdir}/tls
%config %{_sysconfdir}/ld.so.conf.d/%{_nvidia_serie}-%{_lib}.conf
%{_nvidia_libdir}/*.so.*
%{_nvidia_libdir}/libcuda.so
%{_nvidia_libdir}/libnvidia-glcore.so
%{_nvidia_libdir}/tls/*.so*
%exclude %{_libdir}/vdpau/libvdpau.*
%{_libdir}/vdpau/libvdpau_nvidia.so*
%exclude %{_libdir}/vdpau/libvdpau_trace.so*

%files devel
%defattr(-,root,root,-)
%exclude %{_nvidia_libdir}/libXvMCNVIDIA.a
%exclude %{_nvidia_libdir}/libcuda.so
%{_includedir}/nvidia/
%{_nvidia_libdir}/libOpenCL.so
%{_nvidia_libdir}/libnvidia-compiler.so
%{_nvidia_libdir}/libGL.so
%{_nvidia_libdir}/libXvMCNVIDIA.so
%{_nvidia_libdir}/libnvcuvid.so
%{_nvidia_libdir}/libnvidia-ml.so
%{_nvidia_libdir}/libnvidia-opencl.so


%changelog
* Fri Mar 02 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 304.137-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Sep 19 2017 Leigh Scott <leigh123linux@googlemail.com> - 304.137-1
- Update to 304.137
- Fix source URL

* Wed Feb 15 2017 Leigh Scott <leigh123linux@googlemail.com> - 304.135-1
- Update to 304.135

* Wed Dec 14 2016 leigh scott <leigh123linux@googlemail.com> - 304.134-1
- Update to 304.134

* Tue Sep 27 2016 Leigh Scott <leigh123linux@googlemail.com> - 304.132-1
- Update to 304.132

* Thu Nov 19 2015 Nicolas Chauvet <kwizart@gmail.com> - 304.131-1
- Update to 304.131

* Thu Sep 03 2015 Leigh Scott <leigh123linux@googlemail.com> - 304.128-1
- Update to 304.128

* Tue Dec 16 2014 Leigh Scott <leigh123linux@googlemail.com> - 304.125-1
- Update to 304.125

* Thu Jul 10 2014 Nicolas Chauvet <kwizart@gmail.com> - 304.123-1
- Update to 304.123

* Thu Mar 13 2014 Leigh Scott <leigh123linux@googlemail.com> - 304.121-1
- Update to 304.121

* Fri Jan 24 2014 Leigh Scott <leigh123linux@googlemail.com> - 304.119-1
- Update to 304.119

* Sat Dec 28 2013 Leigh Scott <leigh123linux@googlemail.com> - 304.117-4
- remove conditionals

* Fri Dec 27 2013 Leigh Scott <leigh123linux@googlemail.com> - 304.117-3
- fix module path issue with alien msttcore-fonts package

* Mon Dec 16 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.117-2
- Use nvidia symlink for the glx.so

* Sat Dec 14 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.117-1
- Update to 304.117
- Own libXvMCNVIDIA_dynamic.so.1

* Sun Dec 01 2013 Leigh Scott <leigh123linux@googlemail.com> - 304.116-2
- disable glamor module

* Sun Dec 01 2013 Leigh Scott <leigh123linux@googlemail.com> - 304.116-1
- Update to 304.116

* Tue Aug 13 2013 Leigh Scott <leigh123linux@googlemail.com> - 304.108-1
- Update to 304.108

* Sun Jul 21 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-12
- Disable Obsoletes/Provides of nvidia tools until rhbz#985944

* Mon Jul 15 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-11
- Fix typo with libGLcore filter
- Avoid a Virtual Provides for legacy series

* Sat Jul 13 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-9
- Remove empty epoch - may solve rfbz#2874
- Restore nvidia-settings and nvidia-xconfig - rfbz#2852

* Sun Jun 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-8
- Restore the previous xorg.conf in posttrans

* Wed Jun 12 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-5
- Relax kernel flavor cases

* Sat Jun 08 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-4
- Few resync with devel
- Disable execstack fix
- Add support for cuda-driver
- Don't redistribute libnvidia-wfb.so (only needed on EL5).

* Fri Jun 07 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-3
- Add GRUB_GFXPAYLOAD_LINUX=text by default
- Fix PAE kvarriant on uninstall
- Fix grub.cfg path for grub2

* Sun Jun 02 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-2
- Use triggerpostun to re-introduce boot options on rename
- Avoid to use gfxpayload
- Fix missing grubby --default-kernel on PAE kernel

* Sun May 19 2013 Nicolas Chauvet <kwizart@gmail.com> - 304.88-1
- Switch to 304xx serie

* Wed May 01 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:304.88-2
- Add support for cuda

* Thu Apr 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:304.88-1
- Update to 304.88

* Fri Jan 18 2013 Leigh Scott <leigh123linux@googlemail.com> - 1:304.64-5
- move blacklist to %%{_prefix}/lib/modprobe.d/

* Thu Jan 10 2013 Leigh Scott <leigh123linux@googlemail.com> - 1:304.64-4
- Fix preun scriptlet

* Sun Nov 25 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:304.64-3
- Add workaround for incorrect Files section - rfbz#2580

* Thu Nov 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:304.64-1
- Update to 304.64
- Move nvidia xorg libraries to _libdir/nvidia/xorg - rfbz#2264

* Thu Oct 18 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.60-1
- Update to 304.60

* Mon Sep 24 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.51-1
- Update to 304.51

* Sat Sep 15 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.48-1
- Update to 304.48

* Sat Sep 15 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.43-2
- Add missing headers to -devel - rfbz#2475

* Wed Sep 05 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:304.43-1
- Update to 304.43
- Force libvdpau >= 0.5 - rhbz#849486
- Workaround grub2 fb initialization at install time - rfbz#2391
- Reference our own documentation of the driver.

* Tue Aug 14 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.37-1
- Update to 304.37 release

* Sat Aug 04 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.32-1
- Update to 304.32

* Tue Jul 31 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.30-1
- Update to 304.30

* Sat Jul 14 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.22-2
- Add nvidia-cuda-proxy binaries and man file

* Fri Jul 13 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:304.22-1
- Update to 304.22

* Sat Jun 16 2012 leigh scott <leigh123linux@googlemail.com> - 1:302.17-1
- Update to 302.17

* Tue May 22 2012 leigh scott <leigh123linux@googlemail.com> - 1:302.11-1
- Update to 302.11

* Tue May 22 2012 leigh scott <leigh123linux@googlemail.com> - 1:295.53-1
- Update to 295.53

* Sun May 20 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:295.49-2
- Fix %%post when grubby --default-kernel is broken

* Thu May 03 2012 leigh scott <leigh123linux@googlemail.com> - 1:295.49-1
- Update to 295.49

* Wed Apr 11 2012 leigh scott <leigh123linux@googlemail.com> - 1:295.40-1
- Update to 295.40

* Thu Mar 22 2012 leigh scott <leigh123linux@googlemail.com> - 1:295.33-1
- Update to 295.33

* Tue Feb 14 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:295.20-1
- Update to 295.20

* Wed Feb 01 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:295.17-1
- Update to 295.17 (beta)
- Fix kernel options when using grub legacy.
- Change nvidia-kmod-data archive to xz compression

* Sat Dec 31 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:295.09-1
- Update to 295.09 (beta)
- Remove libcuda.so.1 filter - rfbz#2083

* Tue Nov 22 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:290.10-1
- Update to 290.10

* Thu Nov 10 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:290.06-2
- Switch to rd.driver.blacklist from the deprecated rdblacklist on install

* Wed Nov 09 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:290.06-1
- Update to 290.06 beta

* Tue Oct 04 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:285.05.09-1
- Update to 285.05.09

* Sat Aug 27 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:285.03-1
- Update to 285.03

* Tue Aug 02 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:280.13-1
- Update to 280.13

* Sun Jul 24 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:280.11-1
- Update to 280.11

* Tue Jul 05 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:280.04-2
- Fix filter_from_requires/provides libglx.so
- Fix filter_from_requires/provides libcuda.so.1

* Fri Jul 01 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:280.04-1
- Update to 280.04 (beta)

* Tue Jun 14 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:275.09.07-1
- Update to 275.09.07

* Wed Jun 08 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.41.19-1
- Update to 270.41.19
- Use official filter macros - patch from <Jochen herr-schmitt de>

* Sat Apr 30 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.41.06-1
- Update to 270.41.06

* Tue Apr 12 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.41.03-1
- Update to 270.41.03

* Thu Mar 03 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.30-1
- Update to 270.30

* Tue Mar 01 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.29-1
- Update to 270.29

* Tue Feb 22 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.26-1
- Update to 270.26

* Sun Jan 23 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:270.18-1
- Update to 270.18 beta
- Add support for IgnoreABI xorg option

* Fri Jan 21 2011 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.36-1
- Update to 260.19.36
- Restore execstack -c on redistributed binaries
  instead of forcing selinux bool.
  (nvidia-installer clears it at runtime when appropriate).

* Fri Dec 17 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.29-2
- Fix uninstall on kvarriant - rfbz#1559

* Tue Dec 14 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.29-1
- Update to 260.19.29

* Thu Nov 11 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.21-1
- Update to 260.19.21

* Tue Nov 02 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.12-4
- Disable selinux restorecon on initscript.
- Avoid using livna-config-display on fedora 14 and later
  because of rhbz#623742
- Use static workaround
- Explicitely use %%{_isa} dependency from -devel to -libs

* Sun Oct 24 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.12-3
- Improve uninstallation script rfbz#1398
- Fix selinux context on device creation rfbz#1421

* Thu Oct 14 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.12-1
- Update to 260.19.12

* Thu Oct 07 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:260.19.06-1
- Update to 260.19.06 beta

* Thu Sep 16 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:256.53-2
- Fix OpenCL support

* Tue Aug 31 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:256.53-1
- Update to 256.53

* Sat Aug 28 2010 Bob Arendt <rda@rincon.com> - 1:256.52-1
- Update to 265.52 (Adds support for xorg-server driver ABI ver 8, for xorg-server-1.9)

* Mon Aug 16 2010 Bob Arendt <rda@rincon.com> - 1:256.44-1
- Update to 265.44 (Cuda 3.1 compatible)
- libGLcore.so becomes nvidia-libglcore.so

* Thu Jul 08 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:195.36.31-2
- Improve post script as reported in rfbz#1262
- Only blacklist nouveau with grubby on install.

* Wed Jun 16 2010 Nicolas Chauvet <kwizart@gmail.com> - 1:195.36.31-1
- Update to 195.36.31
- Add post section to change boot option with grubby
- Add post section Enabled Selinux allow_execstack boolean.
- Fallback to nouveau instead of nv
- AddARGBGLXVisuals is enabled by default since 195xx serie.

* Sat Apr 24 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 1:195.36.24-1
- Update to 195.36.24

* Sat Mar 27 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 1:195.36.15-1
- Update to 195.36.15
- Use macro for Epoch

* Sun Mar 14 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 1:190.53-4
- Fix multilibs requirements

* Fri Mar 12 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 1:190.53-2
- Bump Epoch - Fan problem in recent release
  http://www.nvnews.net/vbulletin/announcement.php?f=14

* Sat Feb 27 2010 Nicolas Chauvet <kwizart@fedoraproject.org> - 195.36.08-1
- Update to 195.36.08

* Wed Dec 30 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.53-1
- Update to 190.53
- Switch to new libvdpau location in %%{_libdir}/vdpau

* Fri Nov 27 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.42-5
- Remove duplicate desktop file.

* Tue Nov 24 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.42-4
- Use nvidia-xconfig and nvidia-settings built from sources.

* Sat Nov 14 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.42-3
- Remove execstack on nvidia binaries and libraries.

* Tue Nov  3 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.42-2
- Update blacklist-nouveau.conf - rfbz#914

* Sat Oct 31 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 190.42-1
- Update to 190.42

* Sat Oct 10 2009 kwizart < kwizart at gmail.com > - 185.18.36-3
- Exclude libvdpau as it is now a separate package.
- Avoid Requires/Provides of the libGL.so.1 . rfbz#859

* Sat Aug 29 2009 kwizart < kwizart at gmail.com > - 185.18.36-1
- Update to 185.18.36 (final)

* Mon Aug  3 2009 kwizart < kwizart at gmail.com > - 185.18.31-1
- Update to 185.18.31 (final)

* Thu Jul 30 2009 kwizart < kwizart at gmail.com > - 185.18.29-1
- Update to 185.18.29 (final)

* Wed Jul  1 2009 kwizart < kwizart at gmail.com > - 185.18.14-3
- Fix libcuda.so runtime usage - BZ 670#c4
  Workaround for cudart.so wrong behaviour

* Sun Jun  7 2009 kwizart < kwizart at gmail.com > - 185.18.14-2
- blacklist nouveau by default.

* Fri Jun  5 2009 kwizart < kwizart at gmail.com > - 185.18.14-1
- Update to 185.18.14 (final)

* Wed Apr 22 2009 kwizart < kwizart at gmail.com > - 180.51-1
- Update to 180.51 (stable)
- Add 71xx/beta/catalyst Conflicts
- Don't Obsoletes the beta serie anymore (only the newest)

* Fri Apr  3 2009 kwizart < kwizart at gmail.com > - 180.37-3
- Fix x86 Arch for fedora >= 11

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 180.37-2
- rebuild for new F11 features

* Mon Mar  9 2009 kwizart < kwizart at gmail.com > - 180.37-1
- Update to 180.37 (prerelease)

* Thu Feb 26 2009 kwizart < kwizart at gmail.com > - 180.35-2
- Fix Conflicts/Provides with beta
- Obsoltes/Provides for devel

* Wed Feb 25 2009 kwizart < kwizart at gmail.com > - 180.35-1
- Update to 180.35 (prerelease)
- Obsoletes opengl 3.0 beta nserie.

* Sun Feb 22 2009 Stewart Adam <s.adam at diffingo.com> - 180.29-2
- Make devel subpackage depend on lib subpackage of the same arch

* Tue Feb 10 2009 kwizart < kwizart at gmail.com > - 180.29-1
- Update to 180.29 (stable)

* Thu Jan 29 2009 kwizart < kwizart at gmail.com > - 180.27-1
- Update to 180.27 (beta)

* Tue Jan 27 2009 kwizart < kwizart at gmail.com > - 180.25-1
- Update to 180.25 (beta)

* Thu Jan  8 2009 kwizart < kwizart at gmail.com > - 180.22-1
- Update to 180.22 (stable)

* Sat Dec 27 2008 kwizart < kwizart at gmail.com > - 180.18-1
- Update to 180.18 (beta)

* Wed Dec 17 2008 kwizart < kwizart at gmail.com > - 180.16-1
- Update to 180.16 (beta)
- Exclude libXvMCNVIDIA.a
- More accurate -devel subpackage.

* Tue Dec 2 2008 Stewart Adam <s.adam at diffingo.com> - 177.82-2
- Fix upgrade path for nvidia-newest (bz#191)

* Thu Nov 13 2008 kwizart < kwizart at gmail.com > - 177.82-1
- Update to 177.82

* Wed Nov 12 2008 kwizart < kwizart at gmail.com > - 177.80-6
- Obsoletes/Provides xorg-x11-drv-nvidia-newest
- Cleaning
- Improve description

* Tue Nov 4 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-5
- Fix upgrade path for FreshRPMs users

* Mon Oct 27 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-4
- Revert the libs dep change

* Sat Oct 25 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-3
- Remove the libs subpackage's dependency on main package
- Update dependency on livna-config-display

* Sat Oct 18 2008 Stewart Adam <s.adam at diffingo.com> - 177.80-2
- Change dependency of main package to libs subpackage in devel subpackage to
  fix multiarch repo push

* Mon Oct 13 2008 kwizart < kwizart at gmail.com > - 177.80-1
- Update to 177.80
- Move symlinks in -devel
- Fix description

* Sun Oct 05 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 177.78-2
- rebuild for rpm fusion

* Wed Oct 1 2008 Stewart Adam < s.adam at diffingo.com > - 177.78-1
- Update to 177.78 (beta)

* Mon Sep 15 2008 Stewart Adam < s.adam at diffingo.com > - 177.70-1
- Update to 177.70 (beta)

* Thu Jul 31 2008 kwizart < kwizart at gmail.com > - 173.14.12-1
- Update to 173.14.12

* Tue Jun 17 2008 kwizart < kwizart at gmail.com > - 173.14.09-1
- Update to 173.14.09

* Wed May 28 2008 Stewart Adam <s.adam at diffingo.com> - 173.14.05-2
- Only modify modprobe.conf if it exists

* Wed May 28 2008 kwizart < kwizart at gmail.com > - 173.14.05-1
- Update to 173.14.05

* Wed May 14 2008 kwizart < kwizart at gmail.com > - 173.08-2
- Fix libwfb replacement - Not needed on Fedora >= 9

* Thu Apr 10 2008 kwizart < kwizart at gmail.com > - 173.08-1
- Update to 173.08 (beta) - Fedora 9 experimental support
  See: http://www.nvnews.net/vbulletin/showthread.php?t=111460

* Fri Mar  7 2008 kwizart < kwizart at gmail.com > - 171.06-1
- Update to 171.06 (beta)

* Wed Feb 27 2008 kwizart < kwizart at gmail.com > - 169.12-1
- Update to 169.12

* Wed Feb 20 2008 kwizart < kwizart at gmail.com > - 169.09-5
- Fix debuginfo package creation.
- Add libGLcore.so to the filter list.
- Only requires versioned libGL on x86_64 (no problem on x86).

* Thu Feb 7 2008 Stewart Adam <s.adam AT diffingo DOT com> - 169.09-4
- Filter requires on main package so we don't pull in xorg-x11-drv-nvidia*-libs

* Fri Feb  1 2008 kwizart < kwizart at gmail.com > - 169.09-3
- Remove ldconfig call on the main package 
- Remove some old Obsoletes/Provides
- Move the xorg modules to the main package (not needed for multilib)
- Add Requires versioned libGL.so from the right path
- Uses pkg0 instead of pkg2 for x86_64 (and remove the lib32 from our loop).

* Sun Jan 27 2008 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 169.09-2
- let main package require the libs subpackage

* Wed Jan 23 2008 Stewart Adam <s.adam AT diffingo DOT com> - 169.09-1
- Update to 169.09
- Provides nvidia-glx since we obsolete it
- Make .desktop file to pass desktop-file-validate
- Remove libs-32bit and make a proper multiarch -libs package
- Add empty %%build section

* Thu Dec 27 2007 kwizart < kwizart at gmail.com > - 169.07-4
- Provides libcuda.so.1 since AutoProv is disabled for libs-32bit

* Wed Dec 26 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-3
- Backport changes from testing branch (provide cuda libraries)

* Sun Dec 23 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-2
- Require /usr/lib/libGL.so.1.2 to prevent conflicts
- Do provide libGLcore.so.1

* Sat Dec 22 2007 Stewart Adam <s.adam AT diffingo DOT com> - 169.07-1
- Update to 169.07

* Fri Nov 30 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-6
- Don't provide libGL.so.1 (bz#1741)
- Remove shebang for files that are sourced

* Tue Nov 20 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-5
- Add Requires: which (bz#1662)

* Thu Nov 1 2007 Stewart Adam <s.adam AT diffingo DOT com> - 100.14.19-4
- Initscript improvements
- Minor bugfixes with scriptlets (don't echo "already disabled" type messages)

* Fri Oct 12 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.19-3
- Initscript should disable when module isn't found (bz#1671)

* Mon Sep 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.19-2
- Fix %%post if clause (bz#1632)
- Disable the DisableGLXRootClipping option

* Thu Sep 20 2007 kwizart < kwizart at gmail.com > - 100.14.19-1
- Update to 100.14.19
- Improve desktop file
- Sync between F7 and FC-6
- Don't replace user env variable

* Thu Jun 21 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.11-1
- Update to 100.14.11

* Fri Jun 15 2007 Stewart Adam < s.adam AT diffingo DOT com > - 100.14.09-2
- F7 SELinux fixes (continued)
- Add a new post scriptlet to remove those legacy-layout udev files

* Sun Jun 10 2007 kwizart < kwizart at gmail.com > - 100.14.09-1
- Update to Final 100.14.09

* Sat Jun 2 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9762-2
- Don't use legacy udev layout (Thanks Finalzone for the workaround)

* Sun May 27 2007 kwizart < kwizart at gmail.com > - 1.0.9762-1
- Update to 1.0.9762

* Sat Apr 28 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9755-3
- Fixes in the config-display (vendor > majorVendor)

* Fri Mar 9 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9755-2
- Fix up scriptlets a little so that 'Driver already enabled|disabled'
  doesn't always appear on install or remove
- Update *-config-display files for majorVendor and not plain vendor

* Thu Mar 8 2007 kwizart < kwizart at gmail.com > - 1.0.9755-1
- Update to 1.0.9755

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-11
- Bump for new tag
- fi to end if!

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-10
- Bump for new tag

* Sat Feb 24 2007 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9746-9
- Standardize all summaries and descriptions with other nvidia and fglrx
  packages
- Standardize initscript and *config-display with other nvidia and fglrx
  packages
- Move paths from nvidia-glx to nvidia
- Start merge with livna-config-display

* Wed Feb 7 2007 kwizart < kwizar at gmail.com > - 1.0.9746-8
- Update SHA1SUM

* Thu Jan 18 2007 Stewart Adam <s.adam AT diffingo DOT com> - 1.0.9746-7
- Fix initscript empty line problem (#1302)
- Fix typo in the readme
- Put in correct sums into SHA1SUM

* Sun Jan 7 2007 kwizart < kwizart at gmail.com > - 1.0.9746-6
- Quick fix double libs-32bit -p /sbin/ldconfig

* Thu Jan 4 2007 kwizart < kwizart at gmail.com > - 1.0.9746-5
- Create the symlink from libwfb.so to libnvidia-wfb.so.x.y.z 
  the xorg driver search for libwfb.so (it do not use the SONAME).
  http://www.nvnews.net/vbulletin/showthread.php?t=83214

* Wed Jan 3 2007 Stewart Adam < s.adam AT diffingo DOT com  - 1.0.9746-4
- Correct mistake in changelog
- add %%verify to /dev nodes (#1324)
- /etc/profile.d/* are sourced, took away exec bit

* Wed Jan 3 2007 Stewart Adam < s.adam AT diffingo DOT com  - 1.0.9746-3
- Make the 32-bit libs run ldconfig in %%postun and %%post steps
- Possible FIXME for future: "E: xorg-x11-drv-nvidia obsolete-not-provided nvidia-glx'

* Thu Dec 28 2006 kwizart < kwizart at gmail.com > - 1.0.9746-2
- Move the libnvidia-wfb.so lib to the Nvidia xorg extension directory.

* Tue Dec 26 2006 kwizart < kwizart at gmail.com > - 1.0.9746-1
- Update to 1.0.9746 (Final).
- Fix symlink of the new lib which soname is libnvidia-wfb.so.1

* Sun Nov 26 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.9742-3
- use Source0 with "pkg0.run" prefix (smaller)
- use Source1 with "pkg2.run" prefix (cotaints the 32bit libs)

* Thu Nov 23 2006 Stewart Adam < s.adam AT diffingo DOT com > - 1.0.9742-2
- Fix URL
- Change %%description, as NV30 and below no longer supported
- Update nvidia desktop file

* Mon Nov 20 2006 kwizart < kwiart at gmail.com > - 1.0.9742-1
- Update to release 1.0.9742
- Include libdir/xorg/modules/libnvidia-wfb.so.1.0.9742

* Tue Nov 07 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.9629-1
- update to release 1.0.9629

* Tue Oct 31 2006 Dams <anvil[AT]livna.org> - 1.0.9626-3
- Another nvidia-config-display update to fix dumb modules section

* Tue Oct 24 2006 Dams <anvil[AT]livna.org> - 1.0.9626-2
- Yet another updated nvidia-config-display : importing python modules
  we use is usualy a good idea
- Updated nvidia-config-display

* Sun Oct 22 2006 Stewart Adam <s.adam AT diffingo DOT com> - 1.0.9626-1
- update to release 1.0.9626

* Fri Oct 20 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8776-1
- update to 1.0.8776-1 -- fixes CVE-2006-5379

* Thu Aug 24 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8774-1
- Nvidia added a png for nvidia-settings, for-loop adjusted accordingly
- update to release 1.0.8774

* Wed Aug 09 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-6
- small changes to sync with legacy package
- place nvidia-bug-report.sh in /usr/bin

* Mon Aug 07 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-5
- more minor changes to spacing and general layout

* Fri Aug 04 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8762-4
- minor changes to spacing, removal of random tabs, re-arrangements
- remove GNOME category from the desktop file

* Thu May 25 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-3
- Obsolete old kmods

* Thu May 25 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-2
- add missing defattr to files section for sub-package libs-32bit

* Wed May 24 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8762-1
- update to 1.0.8762

* Tue May 16 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8756-3
- Conflict with xorg-x11-drv-fglrx and selinux-policy < 2.2.29-2.fc5
- Ship bug-reporting tool as normal executable and not in %%doc

* Sun May 14 2006 Ville SkyttÃ¤ <ville.skytta at iki.fi> - 1.0.8756-2
- Require nvidia-kmod instead of kmod-nvidia (#970).

* Sat Apr 08 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8756-1
- Update to 8756
- put 32bit libs in their own package

* Wed Mar 29 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8178-9
- make every use of the 'install' command consistent
- tweak nvidia-settings' desktop file slightly

* Thu Mar 23 2006 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 1.0.8178-8
- switch to using modprobe.d rather than editing modprobe.conf directly

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-7
- ExclusiveArch i386 and not %%{ix86} -- we don't want to build for athlon&co

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-6
- drop unused patches

* Sat Mar 18 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-5
- drop 0.lvn

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Wed Feb 08 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.5
- use lib64 in nvidia-config-display on x86-64
- fix path to kernel module in init-script
- add patch from Ville for nvidia-README.Fedora
- match permissions of xorg 7

* Wed Feb 01 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.4
- More fixes

* Tue Jan 31 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.3
- Fix wrong provides

* Mon Jan 30 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.2
- fix path to kernel module in nvidia-glx-init (thx to Dominik 'Rathann'
  Mierzejewski)
- include device files until udev works probably with kernel module

* Sun Jan 22 2006 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 1.0.8178-0.lvn.1
- split into packages for userland and kmod
- rename to xorg-x11-drv-nvidia; yum/rpm should use mesa-libGL{,-devel} then in
  the future when seaching for libGL.so{,.1}
- remove kernel-module part
- remove old cruft
- install stuff without Makefile because it forgets mosts a lot of files anyway

* Thu Dec 22 2005 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 0:1.0.8178-0.lvn.2
- change nvidia-glx.sh and nvidia-glx.csh to point to README.txt rather than README
- reference xorg.conf rather than XF86Config in the init script
- improve readability of instructions and comments, fix some typos
- drop epoch, as it seems to be affecting dependencies according to rpmlint
- tweak the nvidia-settings desktop file so it always shows up on the
  menu in the right location
- add the manual pages for nvidia-settings and nvidia-xconfig
- remove header entries from the nvidia-glx files list. they belong in -devel
- fix changelog entries to refer to 7676 not 7176 (though there was a 7176 x86_64
  release prior to 7174)
- add libXvMCNVIDIA.so
- update to 8178

* Wed Dec 07 2005 Niko Mirthes (straw) <nmirthes AT gmail DOT com> - 0:1.0.8174-0.lvn.1
- add the manual pages for nvidia-settings and nvidia-xconfig
- install the new nvidia-xconfig utility and associated libs

* Mon Dec 05 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.8174-0.lvn.1
- Update to 8174
- desktop entry now Categories=Settings (#665)
- Ship bug-reporting tool in doc (#588)
- Things from Bug 635, Niko Mirthes (straw) <nmirthes AT gmail DOT com>:
-- avoid changing time stamps on libs where possible
-- only add /etc/modprobe.conf entries if they aren't already there
-- add /etc/modprobe.conf entries one at a time
-- only remove /etc/modprobe.conf entries at uninstall, not during upgrade
-- avoid removing any modprobe.conf entries other than our own
-- match Xorg's install defaults where it makes sense (0444)
-- a few other minor tweaks to the files lists

* Sun Sep 04 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.3
- Conflics with nvidia-glx-legacy
- Integrate some minor correction suggested by Niko Mirthes
  <nmirthes AT gmail DOT com> in #475

* Fri Aug 26 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.2
- Rename src5: nvidia.init to nvidia-glx-init
- Fix correct servicename in nvidia-glx-init
- Run nvidia-glx-init before gdm-early-login; del and readd the script
  during post

* Sun Aug 21 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7676-0.lvn.1
- Update to 7676
- Lots of cleanup from me and Niko Mirthes <nmirthes AT gmail DOT com>
- add NVreg_ModifyDeviceFiles=0 to modprobe.conf (Niko)
- Drop support for FC2
- Nearly proper Udev-Support with workarounds around FC-Bug 151527

* Fri Jun 17 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.5
- Slight change of modprobe.conf rexexp

* Thu Jun 16 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.4
- Fixed a critical bug in modprobe.conf editing where all lines starting with alias and
  ending with then a word starting with any of the letters n,v,i,d,i,a,N,V,r,e is removed.

* Mon Jun 13 2005 Thorsten Leemhuis <fedora AT leemhuis DOT info> - 0:1.0.7174-0.lvn.3
- Adjust kenrnel-module-stuff for FC4
- Ship both x86 and x64 in the SRPM

* Sun Jun 12 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.2
- Only create 16 devices
- Put libXvMCNVIDIA.a in -devel
- Don't remove nvidia options in /etc/modprobe.conf
- Make ld.so.conf file config(noreplace)
- Use same directory permissions as the kernel

* Sat Apr 2 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7174-0.lvn.1
- New upstream release, 7174

* Wed Mar 30 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.5
- Added x86_64 support patch from Thorsten Leemhuis

* Wed Mar 23 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.4
- Fix kernel module permissions again (644)
- Only create 16 /dev/nvidia* devices, 256 is unnecessary

* Fri Mar 18 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.3
- Fixed kernel-module permissions

* Thu Mar 17 2005 Dams <anvil[AT]livna.org> 0:1.0.7167-0.lvn.2
- Removed provides on kernel-module and kernel-modules

* Sat Mar 05 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.7167-0.lvn.1
- New upstream release 1.0.7167
- Added patch from http://www.nvnews.net/vbulletin/showthread.php?t=47405
- Removed old patch against 2.6.9

* Sat Feb 05 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.7
- Added a number of post-6629 patches from http://www.minion.de/files/1.0-6629
- Fixed permissions of nvidia/nvidia.ko

* Fri Jan 21 2005 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.6
- Fix incorrect MAKDEV behaviour and dependency

* Tue Nov 30 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.4
- Fixed creation of /dev/nvidia* on FC2

* Sat Nov 27 2004 Dams <anvil[AT]livna.org> - 0:1.0.6629-0.lvn.3
- Dont try to print kvariant in description when it's not defined.

* Sun Nov 21 2004 Thorsten Leemhuis <fedora at leemhuis dot info> - 0:1.0.6629-0.lvn.2
- resulting kernel-module package now depends again on /root/vmlinuz-<kernelver>
- Use rpmbuildtags driverp and kernelp

* Sat Nov 06 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6629-0.lvn.1
- New upstream version, 1.0-6629
- Build without kernel-module-devel by default

* Fri Oct 29 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.6
- Make n-c-display handle misc problems in a better way
- Fixed wrong icon file name in .desktop file
- Re-added the mysteriously vanished sleep line in the init script
  when kernel module wasn't present

* Fri Oct 22 2004 Thorsten Leemhuis <fedora at leemhuis dot info> - 0:1.0.6111-0.lvn.5
- Use fedora-kmodhelper in the way ntfs or ati-fglrx use it
- Allow rpm to strip the kernel module. Does not safe that much space ATM but
  might be a good idea
- Allow to build driver and kernel-module packages independent of each other
- Some minor spec-file changes

* Thu Oct 21 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.4
- udev fixes
- Incorporated fix for missing include line in ld.so.conf from ati-fglrx spec (T Leemhuis)

* Sun Sep 19 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.3
- Remove FC1/kernel 2.4 compability
- Rename srpm to nvidia-glx
- Build with kernel-module-devel

* Sun Aug 15 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.2
- Restore ldsoconfd macro
- Disable autoamtic removal of scripted installation for now; needs testing

* Sat Aug 14 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6111-0.lvn.1
- Upstream release 6111
- Fixed init script (again)

* Tue Aug  3 2004 Dams <anvil[AT]livna.org> 0:1.0.6106-0.lvn.4
- ld.so.conf.d directory detected by spec file
- Using nvidialibdir in nvidia-glx-devel files section
- Got rid of yarrow and tettnang macros
- libGL.so.1 symlink in tls directory always present

* Mon Jul 19 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.3
- Fixed script bug that would empty prelink.conf
- Added symlink to non-tls libGL.so.1 on FC1

* Tue Jul 13 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.3
- Updated init script to reflect name change -xfree86 -> -display

* Mon Jul 12 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.2
- Fixed backup file naming

* Sun Jul 11 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2.1
- Restore working macros
- Always package the gui tool

* Sun Jul 11 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.2
- Renamed nvidia-config-xfree86 to nvidia-config-display
- Fixed symlinks
- Use ld.so.conf.d on FC2
- Remove script installation in pre
- Use system-config-display icon for nvidia-settings
- 2 second delay in init script when kernel module not found
- Make nvidia-config-display fail more gracefully
- Add blacklist entry to prelink.conf on FC1

* Mon Jul 05 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.6106-0.lvn.1
- New upstream release
- First attempt to support FC2
- Dropped dependency on XFree86

* Mon Feb 09 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.5336-0.lvn.3
- Use pkg0

* Sun Feb 08 2004 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.5336-0.lvn.2
- New Makefile variable SYSSRC to point to kernel sources.
- kmodhelper fixes.

* Fri Jan 30 2004 Keith G. Robertson-Turner <nvidia-devel[AT]genesis-x.nildram.co.uk> 0:1.0.5336-0.lvn.1
- New upstream release
- Removed (now obsolete) kernel-2.6 patch
- Install target changed upstream, from "nvidia.o" to "module"
- Linked nv/Makefile.kbuild to (now missing) nv/Makefile

* Sun Jan 25 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.18
- Updated nvidia-config-display
- Now requiring pyxf86config

* Mon Jan 19 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.17
- Added nvidiasettings macro to enable/disable gui packaging

* Mon Jan 19 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.16
- Updated minion.de patches
- Added some explicit requires
- Test nvidia-config-xfree86 presence in kernel-module package
  scriptlets

* Mon Jan 12 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.15
- Updated Readme.fedora
- nvidia-glx-devel package

* Sat Jan  3 2004 Dams <anvil[AT]livna.org> 0:1.0.5328-0.lvn.14
- Hopefully fixed kernel variant thingy

* Fri Jan  2 2004 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.13
- Support for other kernel variants (bigmem, etc..)
- Changed URL in Source0

* Tue Dec 30 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.13
- Dropped nvidia pkgX information in release tag.

* Tue Dec 30 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.12.pkg0
- Renamed kernel module package in a kernel-module-nvidia-`uname -r` way
- Using fedora.us kmodhelper for kernel macro
- Using nvidia pkg0 archive

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.11.pkg1
- kernel-module-nvidia package provides kernel-module
- We wont own devices anymore. And we wont re-create them if they are
  already present

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.10.pkg1
- Yet another initscript update. Really.
- Scriptlets updated too

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.9.pkg1
- Fixed alias in modprobe.conf for 2.6

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.8.pkg1
- Another initscript update

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.7.pkg1
- kernel module requires kernel same kversion
- initscript updated again
- Dont conflict, nor obsolete XFree86-Mesa-libGL. Using ld.so.conf to
  make libGL from nvidia first found. Hope Mike Harris will appreciate.

* Sun Dec 21 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.6.pkg1
- kernel-module-nvidia requires kernel same version-release

* Sat Dec 20 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.6.pkg1
- Updated initscript

* Fri Dec 19 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.lvn.5.pkg1
- lvn repository tag

* Fri Dec 19 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.5.pkg1
- Added initscript to toggle nvidia driver according to running kernel
  and installed kernel-module-nvidia packages
- Updated scriptlets

* Thu Dec 18 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.4.pkg1
- Arch detection
- Url in patch0

* Tue Dec 16 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.3.pkg1
- Desktop entry for nvidia-settings
- s/kernel-module-{name}/kernel-module-nvidia
- nvidia-glx doesnt requires kernel-module-nvidia-driver anymore
- Using modprobe.conf for 2.6 kernel
- Hopefully fixed symlinks

* Mon Dec 15 2003 Dams <anvil[AT]livna.org> 0:1.0.4620-0.fdr.2.pkg1
- Building kernel module for defined kernel
- kernel module for 2.6 is nvidia.ko
- Patch not to install kernel module on make install
- Updated patch for 2.6
- depmod in scriptlet for defined kernel
- nvidia-glx conflicting XFree86-Mesa-libGL because we 0wn all its
  symlink now
- Dont override libGL.so symlink because it belongs to XFree86-devel
- Added nvidia 'pkgfoo' info to packages release
- Spec file cleanup

* Fri Dec 12 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4620-0.fdr.2
- Fixed repairing of a link in post-uninstall
- Obsolete Mesa instead of Conflict with it, enables automatic removal.

* Mon Dec 08 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4620-0.fdr.1
- Added support for 2.6 kernels
- Cleaned up build section, removed the need for patching Makefiles.
- Added missing BuildReq gcc32
- Don't package libs twice, only in /usr/lib/tls/nvidia
- Made config cript executable and put it into /usr/sbin
- Moved kernel module to kernel/drivers/video/nvidia/
- Fixed libGL.so and libGLcore.so.1 links to allow linking against OpenGL libraries

* Mon Dec 08 2003 Keith G. Robertson-Turner <nvidia-devel at genesis-x.nildram.co.uk> - 0:1.0.4620-0.fdr.0
- New beta 4620 driver
- New GUI control panel
- Some minor fixes

* Thu Nov 20 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.10.1
- Finally fixed SMP builds.

* Wed Nov 19 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.9
- Don't make nvidia-glx depend on kernel-smp

* Tue Nov 18 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.8
- Some build fixes

* Tue Nov 11 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.7
- Added CC=gcc32
- Fixed upgrading issue
- Added driver switching capabilities to config script.

* Fri Nov 07 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.4
- Added conflict with XFree86-Mesa-libGL.
- Disabled showing of the README.Fedora after installation.

* Sun Oct 12 2003 Peter Backlund <peter dot backlund at home dot se> - 0:1.0.4496-0.fdr.3
- Added NVidia configuration script written in Python.
- Some cleanup of files section
- For more info, see https://bugzilla.fedora.us/show_bug.cgi?id=402

* Tue Jul 08 2003 Andreas Bierfert (awjb) <andreas.bierfert[AT]awbsworld.de> - 0:1.0.4363-0.fdr.2
- renamed /sbin/makedevices.sh /sbin/nvidia-makedevices.sh ( noticed by
  Panu Matilainen )
- Fixed name problem
* Sun Jun 22 2003 Andreas Bierfert (awjb) <andreas.bierfert[AT]awbsworld.de> - 0:1.0.4363-0.fdr.1
- Initial RPM release, still some ugly stuff in there but should work...
