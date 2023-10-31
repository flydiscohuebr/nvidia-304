#
# spec file for package nvidia-gfxG02
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

# kABI symbols are no longer generated with openSUSE >= 13.1, since they
# became useless with zypper's 'multiversion' feature enabled for the kernel
# as default (multiple kernels can be installed at the same time; with
# different kABI symbols of course!). So it has been decided to match on the
# uname output of the kernel only. We cannot use that one for NVIDIA, since we
# only build against GA kernel. So let's get rid of this requirement.
#
%global __requires_exclude kernel-uname-r*

Name:           nvidia-gfxG02
Version:        304.137
Release:        lp154.41.1
License:        SUSE-NonFree
Summary:        NVIDIA graphics driver kernel module for GeForce 6xxx and newer GPUs
URL:            https://www.nvidia.com/object/unix.html
Group:          System/Kernel
Source0:        http://download.nvidia.com/XFree86/Linux-x86/%{version}/NVIDIA-Linux-x86-%{version}.run
Source1:        http://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source3:        preamble
Source6:        fetch.sh
Source7:        README
Source8:        kmp-filelist
Source10:       kmp-post.sh
Source12:       my-find-supplements
Source13:       kmp-preun.sh
Source15:       pci_ids-%{version}.legacy
Source16:       nvidia-gfxG02.rpmlintrc
Patch1:         NVIDIA_kernel-define_linux.diff
Patch2: 0001-disable-mtrr-4.3.patch
Patch3: 0002-pud-offset-4.12.patch
Patch4: 0003-nvidia-drm-pci-init-4.14.patch
Patch5: 0004-timer-4.15.patch
Patch6: 0005-usercopy-4.16.patch
Patch7: 0006-do_gettimeofday-5.0.patch
Patch8: 0007-subdirs-5.3.patch
Patch9: 0008-on-each-cpu-5.3.patch
Patch10: 0009-remove-drmp-5.5.patch
Patch11: 0010-proc-ops-5.6.patch
Patch12: 0011-kernel-5.7.0-setmemoryarray.patch
Patch13: 0012-kernel5.8.patch
Patch14: 0013-kernel5.9.patch
Patch15: 0014-import-drm_legacy_pci_init-exit-from-src-linux-5.9.1.patch
Patch16: 0015-add-static-and-nv_-prefix-to-copied-drm-legacy-bits.patch
Patch17: 0016-fix-mistake.patch
Patch18: 0016-vmalloc5.9.patch
Patch19: 0017-patch-14-kernel-5.11.patch
Patch20: 0018-kernel5.14.patch
Patch21: 0019-kernel-5.16.patch
Patch22: 0020-kernel-5.17.patch
Patch23: 0021-kernel-5.18-opensusedit.patch
Patch24: 0022-kernel-6.0-opensusedit.patch
Patch25: 0023-kernel-6.2.patch
Patch26: 0024-kernel-6.3.patch
Patch27: 0025-kernel-6.5.patch
#Patch3:         u_nvidia_mtrr_k4_3.patch
#Patch4:         xf86-video-nvidia-legacy-0010-kernel-4.14.patch
#Patch5:         xf86-video-nvidia-legacy-0010-kernel-4.15.patch
#Patch6:         nvidia-legacy-304xx-304.137-linux5.patch
NoSource:       0
NoSource:       1
NoSource:       6
NoSource:       7
BuildRequires:  kernel-source
BuildRequires:  kernel-syms
#%if 0%{?sle_version} >= 120400 && !0%{?is_opensuse} 
#BuildRequires:  kernel-syms-azure
#%endif
BuildRequires:  module-init-tools
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
ExclusiveArch:  %ix86 x86_64
# patch the kmp template
%define kmp_template -t
%define kmp_filelist kmp-filelist
%define kmp_post kmp-post.sh
%define kmp_preun kmp-preun.sh
%define kmp_template_name /usr/lib/rpm/kernel-module-subpackage
%(sed -e '/^%%post\>/ r %_sourcedir/%kmp_post' -e '/^%%preun\>/ r %_sourcedir/%kmp_preun' -e '/^Provides: multiversion(kernel)/d' %kmp_template_name >%_builddir/nvidia-kmp-template)
# moved from %kmp_post snippet to this place (boo#1145316)
%(sed -i '/^%%posttrans/i \
exit $RES' %_builddir/nvidia-kmp-template)
# Leap 42.3/sle12-sp3 needs this to recompile module after having
# uninstalled drm-kmp package (%triggerpostun)
%if 0%{?suse_version} < 1320 && 0%{?sle_version} >= 120300
%(cp %_builddir/nvidia-kmp-template %_builddir/nvidia-kmp-template.old)
%(echo "%triggerpostun -n %%{-n*}-kmp-%1 -- drm-kmp-default" >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_preun               >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_post                >> %_builddir/nvidia-kmp-template)
%(echo 'nvr=%%{-n*}-kmp-%1-%_this_kmp_version-%%{-r*}' >> %_builddir/nvidia-kmp-template)
%(echo 'wm2=/usr/lib/module-init-tools/weak-modules2' >> %_builddir/nvidia-kmp-template)
%(echo 'if [ -x $wm2 ]; then' >> %_builddir/nvidia-kmp-template)
%(echo '    %%{-b:KMP_NEEDS_MKINITRD=1} INITRD_IN_POSTTRANS=1 /bin/bash -${-/e/} $wm2 --add-kmp $nvr' >> %_builddir/nvidia-kmp-template)
%(echo 'fi' >> %_builddir/nvidia-kmp-template)
# moved from %kmp_post snippet to this place (boo#1145316)
%(echo 'exit $RES' >> %_builddir/nvidia-kmp-template)
# Let all initrds get generated by regenerate-initrd-posttrans
# if drm-kmp-default gets uninstalled
%(echo "%%{?regenerate_initrd_posttrans}"  >> %_builddir/nvidia-kmp-template)
%endif
%define kver %(for dir in /usr/src/linux-obj/*/*/; do make %{?jobs:-j%jobs} -s -C "$dir" kernelversion; break; done |perl -ne '/(\\d+)\\.(\\d+)\\.(\\d+)?/&&printf "%%d%%02d%%03d\\n",$1,$2,$3')
%define x_flavors kdump um debug xen xenpae
%kernel_module_package %kmp_template %_builddir/nvidia-kmp-template -p %_sourcedir/preamble -f %_sourcedir/%kmp_filelist -x %x_flavors

# supplements no longer depend on the driver
%define pci_id_file %_sourcedir/pci_ids-%version.legacy
# rpm 4.9+ using the internal dependency generators
%define __ksyms_supplements %_sourcedir/my-find-supplements %pci_id_file %name
# older rpm
%define __find_supplements %_sourcedir/my-find-supplements %pci_id_file %name

%description
This package provides the closed-source NVIDIA graphics driver kernel
module for GeForce 6xxx and newer GPUs.

%package KMP
License:        SUSE-NonFree
Summary:        NVIDIA graphics driver kernel module for GeForce 6xxx and newer GPUs
Group:          System/Kernel

%description KMP
This package provides the closed-source NVIDIA graphics driver kernel
module for GeForce 6xxx and newer GPUs.

%prep
echo "kver = %kver"
%setup -T -c %{name}-%{version}
%ifarch %ix86
 sh %{SOURCE0} -x
%endif
%ifarch x86_64
 sh %{SOURCE1} -x
%endif
#rm -rf NVIDIA-Linux-x86*-%{version}-*/usr/src/nv/precompiled
mkdir -p source/%{version}
cp NVIDIA-Linux-x86*-%{version}/kernel/* source/%{version} || :
pushd source/%{version}
 # mark support as external
 echo "nvidia.ko external" > Module.supported
 ln -s Makefile.kbuild Makefile
 ### Bug 123456
 #sed -i /0x1234/d %_sourcedir/pci_ids-%{version}
 #sed -i /0x1234/d %_sourcedir/pci_ids-%{version}.new
 ### Bugs 768020, 751730
 cat >> %_sourcedir/pci_ids-%{version} << EOF
0x0FFB 0x0FFB
0x0FFC 0x0FFC
EOF
 cat >> %_sourcedir/pci_ids-%{version}.new << EOF
0x0FFB 0x0FFB
0x0FFC 0x0FFC
EOF
 chmod 755 %_sourcedir/my-find-supplements*
%patch1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
rm -f *.orig
popd
mkdir obj
sed -i -e 's,-o "$ARCH" = "x86_64",-o "$ARCH" = "x86_64" -o "$ARCH" = "x86",' source/*/conftest.sh

%build
export EXTRA_CFLAGS='-DVERSION=\"%{version}\"'
for flavor in %flavors_to_build; do
    src=/lib/modules/$(make %{?jobs:-j%jobs} -siC %{kernel_source $flavor} kernelrelease)/source
    if ! test -d "$src"; then
        src=/usr/src/linux
    fi
    rm -rf obj/$flavor
    touch $PWD/source/%{version}/.nv-kernel.o.cmd
    cp -r source obj/$flavor
    make %{?jobs:-j%jobs} -C /usr/src/linux-obj/%_target_cpu/$flavor modules M=$PWD/obj/$flavor/%{version} SYSSRC="$src" SYSOUT=/usr/src/linux-obj/%_target_cpu/$flavor
    pushd $PWD/obj/$flavor/%{version}
    make %{?jobs:-j%jobs} -f Makefile.kbuild nv-linux.o SYSSRC="$src" SYSOUT=/usr/src/linux-obj/%_target_cpu/$flavor
    popd
done

%install
### do not sign the ghost .ko file, it is generated on target system anyway
export BRP_PESIGN_FILES=""
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=updates
for flavor in %flavors_to_build; do
    export SYSSRC=/lib/modules/$(make %{?jobs:-j%jobs} -siC %{kernel_source $flavor} kernelrelease)/source
    if ! test -d "$SYSSRC"; then
        SYSSRC=/usr/src/linux
    fi
    make %{?jobs:-j%jobs} -C /usr/src/linux-obj/%_target_cpu/$flavor modules_install M=$PWD/obj/$flavor/%{version}
    #install -m 644 $PWD/obj/$flavor/%{version}/{nv-linux.o,nv-kernel.o} \
    #  %{buildroot}/lib/modules/*-$flavor/updates
    mkdir -p %{buildroot}/usr/src/kernel-modules/nvidia-%{version}-${flavor}
    touch %{buildroot}/usr/src/kernel-modules/nvidia-%{version}-${flavor}/.nv-kernel.o.cmd
    cp source/%{version}/* %{buildroot}/usr/src/kernel-modules/nvidia-%{version}-${flavor}
done
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
for flavor in %flavors_to_build; do
  echo "blacklist nouveau" > %{buildroot}%{_sysconfdir}/modprobe.d/nvidia-$flavor.conf
done
%changelog
* Fri Oct  1 2021 Stefan Dirsch <sndirsch@suse.com>
- cleanup: remove support for sle10 and sle11
* Tue Sep 21 2021 Stefan Dirsch <sndirsch@suse.com>
- fixed build against Devel_Kernel_master
* Fri Jun  5 2020 Stefan Dirsch <sndirsch@suse.com>
- no longer require 3ddiag, which is no longer needed at all ...
* Thu Mar 12 2020 Stefan Dirsch <sndirsch@suse.com>
- using /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G0X.conf now,
  so a driver series update (when user ignores the explicit driver
  series conflict!) no longer will result in no access to NVIDIA
  devices (boo#1165987)
* Mon Jan  6 2020 Stefan Dirsch <sndirsch@suse.com>
- added "azure" kernel flavor
* Mon Aug 19 2019 Stefan Dirsch <sndirsch@suse.com>
- moved exit from %%post snippet file to specfile after running
  weak-modules2 (boo#1145316)
* Mon Jul  8 2019 Stefan Dirsch <sndirsch@suse.com>
- kmp-post.sh/kmp-trigger.sh
  * exit with error code 1 from %%post/%%trigger, if kernel module
    build/install fails (boo#1131028)
* Tue Jul  2 2019 Stefan Dirsch <sndirsch@suse.com>
- no longer touch xorg.conf on suse >= sle12
* Thu Jun 13 2019 Stefan Dirsch <sndirsch@suse.com>
- making use of parallel builds with make's -j option
* Fri Oct 12 2018 sndirsch@suse.com
- let x11-video-nvidiaG02 %%post-require xorg-x11-server, since on
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
- xf86-video-nvidia-legacy-0010-kernel-4.14.patch
  * fixes build against Kernel 4.12 (used on sle12-sp4)
* Sun Sep 23 2018 sndirsch@suse.com
- no longer alter, i.e. strip NVIDIA's libraries
* Thu May 17 2018 sndirsch@suse.com
- workaround build failure of kernelrelease target on sle12-sp4
  (boo#1093333)
* Mon Nov 13 2017 sndirsch@suse.com
-  added libelf-devel to BuildRequires for Tumbleweed
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
* Thu Aug 17 2017 sndirsch@suse.com
- removed wrong provides to drm-kmp (only obsoletes should be used
  here!)
* Fri Jul 28 2017 sndirsch@suse.com
- add patch nvidia-304-4.10.patch to fix build with kernel 4.10
  and above (based on nvidia-340-4,10 patch taken from nvidia forum)
* Mon Jun 19 2017 sndirsch@suse.com
- provide/obsolete drm-kmp-<flavor> on sle12-sp3/Leap 42.3 (boo#1044816)
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
- u_gcc4.8.5.patch
  * required on sle12-sp2/Leap 42.2 (gcc 4.8.5)
* Tue Jan  3 2017 sndirsch@suse.com
- u_nvidia_mtrr_k4_3.patch
  * make sure deprecated kernel APIs for mtrr are no longer used
    on kernel >= 4.3, since they are no longer exported
    (bnc#1017755)
* Tue Dec 13 2016 sndirsch@suse.com
- update to driver release 304.134
  * Added support for X.Org xserver ABI 23 (xorg-server 1.19)
  * Fixed a bug that allowed nvidia-installer to attempt loading kernel
    modules that were built against non-running kernels.
* Fri Sep 30 2016 sndirsch@suse.com
- %%post: create symlinks and /usr/lib/tmpfiles.d snippet for udev so
  nvidia devices will get user ACLs by logind later (bnc#1000625)
- %%preun cleanup: remove tmpfiles.d snippet
* Mon Sep 26 2016 sndirsch@suse.com
- update to driver release 304.132
  * Added /var/log/dmesg to the list of paths which are searched by
    nvidia-bug-report.sh for kernel messages.
  * Fixed a bug that caused kernel panics when using the NVIDIA driver
    on v4.5 and newer Linux kernels built with CONFIG_DEBUG_VM_PGFLAGS.
  * Updated nvidia-installer to support ncurses version 6.x.
* Wed Jun  8 2016 sndirsch@suse.com
- fixed build and installation of kernel modules on target system
* Wed May 25 2016 sndirsch@suse.com
- refixed build against sle10-sp4 (patch by mmarek)
* Mon May 23 2016 mmarek@suse.cz
- Fix build if the source tree is not /usr/src/linux (needed to
  build against kernel-source-vanilla or kernel-source-rt).
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
- supersedes 304.125-kernel-4.0.patch
* Tue Jun 16 2015 sndirsch@suse.com
- added Obsoletes/Conflicts for G01 and older (bnc#802624)
* Mon Jun 15 2015 sndirsch@suse.com
-  avoid accidental removal of G<n+1> alternative (bnc#802624)
* Fri May  8 2015 sndirsch@suse.com
- 304.125-kernel-4.0.patch
  * fixes build for kernel 4.0
* Thu Apr  2 2015 sndirsch@suse.com
- remove "multiversion(kernel)" from provides (bnc#925437)
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
* Tue Jun  3 2014 sndirsch@suse.com
- update to driver release 304.121
  * Improved compatibility with recent Linux kernels.
  * Fixed a bug that prevented the NVIDIA implementation of the
    Xinerama extension protocol requests from being used when RandR
    was enabled.
* Fri Apr 11 2014 sndirsch@suse.com
- disable signing of .ko file
* Tue Feb 25 2014 sndirsch@suse.com
- update to driver release 304.119
  * Fixed a crash when using WebGL in Firefox with a Geforce 6 GPU.
* Wed Feb 12 2014 sndirsch@suse.com
- removed useless "nvidia-gfxG02-kmp" Provides in order to fix
  build on factory/sle12
- enhanced rpmlintrc in order to to fix build on sle12
* Thu Jan 16 2014 sndirsch@suse.com
- update to driver release 304.117
  * added support for xorg-server 1.15
  * supersedes get_num_physpages_304.patch
* Fri Nov  1 2013 sndirsch@suse.com
- get_num_physpages_319.patch
  * official patch by NVIDIA to accomplish compatibily to kernel 3.11
- obsoletes no longer applied unofficial and considered wrong patch
  3.11-num_physpages.patch
* Thu Oct 17 2013 sndirsch@suse.com
- disabled 3.11-num_physpages.patch, since it is considered wrong:
  "The problem with this patch is that it replaces a variable
  (num_physpages) with the address of a function (get_num_physpages).
  It allows the driver to compile, but is functionally incorrect. Any
  code that exercises NV_NUM_PHYSPAGES can't be trusted to operate
  correctly." (comment by NVIDIA); waiting for correct patch by NVIDIA
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
- obsoletes nvidia-drivers-linux-3.11-full.patch.txt
- added 3.11-num_physpages.patch to fix build with kernel 3.11
* Tue Oct  8 2013 sndirsch@suse.com
- ignore missing supplements to fix build for openSUSE 12.3
* Thu Sep 19 2013 sndirsch@suse.com
- get rid of 'uname' requirement in KMP (see comment in specfile
  for details)
* Thu Jul 25 2013 sndirsch@suse.com
- use kernel-source instead of kernel-<flavor>-devel as prereq
  on sle <= 10 (bnc#829352)
* Fri Jul 19 2013 ro@suse.de
- add nvidia-drivers-304.88-linux-3.10.patch to fix build with
  kernel 3.10.0 and above
* Fri May 17 2013 ro@suse.de
- arch is "x86" with 3.9 kernels
* Thu Apr  4 2013 sndirsch@suse.com
- update to driver release 304.88
  Fixed CVE-2013-0131: NVIDIA UNIX GPU Driver ARGB Cursor Buffer
  Overflow in "NoScanout" Mode.  This buffer overflow, which occurred
  when an X client installed a large ARGB cursor on an X server
  running in NoScanout mode, could cause a denial of service (e.g.,
  an X server segmentation fault), or could be exploited to achieve
  arbitrary code execution.
  For more details, see:
  http://nvidia.custhelp.com/app/answers/detail/a_id/3290
* Thu Apr  4 2013 sndirsch@suse.com
- kmp-post.sh: Ensure that the updates directory exists
  * If /lib/modules/`uname -r` does not already have an "updates"
    directory, then nvidia.ko will get copied as a file named
    "updates", instead of being copied into a directory named
    "updates". To prevent this, make sure that the "updates"
    directory already exists before installing nvidia.ko to it.
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
- refreshed NVIDIA_kernel-define_linux{,-x86}.diff
* Mon Feb 18 2013 ro@suse.de
- define __linux__ when compiling kernel module
* Wed Jan 23 2013 sndirsch@suse.com
- introduced .legacy pci_ids file required for creating G03 package
  combo and (open)SUSE <= 12.3
* Wed Jan  2 2013 sndirsch@suse.com
- major cleanup, i.e. removed obsolete patches
  * NVIDIA_kernel-2.6.25.diff
  * conftest.sh-generated_asm.diff
  * conftest.sh.diff
  * conftest.sh.diff.xen-11.0
  * conftest.sh.diff.xen-11.1-i586
  * no-xen-sanity-check.diff
  * nv-fix-xen.diff
  * patch_nvidia_295_40_run_for_3.4
- no longer build Xen kernel modules on any platform/distribution
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
* Wed Nov  7 2012 sndirsch@suse.com
- prerequire kernel-<flavor>-devel instead of kernel-devel to fix
  build during installation
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
* Mon Oct  8 2012 sndirsch@suse.com
- build glue layer during %%post
* Thu Aug 30 2012 sndirsch@suse.com
- always let x11-video-nvidiaG02 require the correct version of
  nvidia-gfxG02-kmp, since via the preamble file we do the
  provides now version-wise
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
- 304.37 has become certified
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
- fixed build for Kernel >= 3.3 and < 3.4 (bnc#761814)
* Fri May 11 2012 sndirsch@suse.com
- update to 295.49
  * Added support for the following GPU: GeForce GTX 690
  * Fixed a problem where starting, stopping, and moving OpenGL
    application windows was very slow on Quadro FX 4600,
    Quadro FX 5600, GeForce 8800 GTX, GeForce 8800 GTS, and
    GeForce 8800 Ultra.
  * Fixed an OpenGL performance regression which affected
    Geforce 6 and Geforce 7 series integrated GPUs.
* Fri May 11 2012 sndirsch@suse.com
- patch_nvidia_295_40_run_for_3.4
  * fixes build with kernel 3.4
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
* Wed Mar  7 2012 ro@suse.de
- fix compile on 3.3.0rc kernel
  add another include path in conftest.sh
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
- obsoletes NVIDIA_kernel-1.0-9625-NOSMBUS.diff.txt
* Tue Dec 20 2011 ro@suse.de
- make kmp packages non-conflicting
* Thu Nov 24 2011 sndirsch@suse.com
- update to 290.10
  * adds support for GeForce GTX 460 SE v2 and GeForce 510
  * bugfixes; among these is the following
  - Fixed a regression that caused blank/white windows when
    exhausting video memory on GeForce 6 and 7 series GPUs
    while using composited desktops.
- adjusted nv-fix-xen.dif
* Wed Nov 23 2011 mmarek@suse.cz
- Make the custom find-supplements script work with the internal
  dependency generator in rpm 4.9 (bnc#731382).
* Wed Nov 23 2011 mmarek@suse.cz
- Do not maintain modified copies of the find-supplements* files,
  but instead run rpm's scripts and filter their output. Also,
  avoid patching scripts in sourcedir (bnc#731382).
* Mon Oct 17 2011 ro@suse.de
- use more reliable version for kernel-version define
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
* Mon Jul 25 2011 ro@suse.com
- update to 275.19
  * Added support for the following GPU:
    GeForce GT 540M
  * Fixed memory error and abort reported by glibc when running
    the application FieldView from Intelligent Light.
  * Fixed an OpenGL driver bug that caused an application crash
    when running Altair HyperMesh.
  * Fixed a performance problem when switching between stereo and
    monoscopic rendering in the application Smoke.
  * Fixed poor X driver handling of pixmap out of memory scenarios.
  * Fixed an interrupt handling deficiency that could lead to
    performance and stability problems when many NVIDIA GPUs shared
    few IRQs.
  * Fixed bugs in the VDPAU presentation queue that could cause GPU
    errors and hangs when destroying a presentation queue.
    This happens when exiting applications, and also when toggling
    to and from full-screen mode in Adobe Flash.
* Fri Jul  8 2011 ro@suse.de
- build fixes for kernel 3.0.rc5
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
* Fri Apr 29 2011 sndirsch@novell.com
- update to 270.41.06
  * Added support for new GeForce/Quadro/NVS/Tesla GPUs
  * Fixed a bug causing the X server to hang every 49.7 days on
    32-bit platforms.
  * Fixed a bug that caused some GPUs to stop responding when the
    X Server was started. All GPUs are susceptible, but the failure
    was primarily seen on GF104 and GF106 boards.
* Wed Apr 27 2011 sndirsch@novell.com
- update to 270.30
  * Added support for GeForce GTX 560 Ti
  * Added new shared library: libnvidia-ml.so.
    NVML provides programmatic access to static information and
    monitoring data for NVIDIA GPUs, as well as limited managment
    capabilities. It is intended for use with Tesla compute products.
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
* Sat Oct 23 2010 sndirsch@novell.com
- fixed build on openSUSE 11.1
* Fri Oct 15 2010 sndirsch@novell.com
- update to 260.19.12
  * adds libnvcuvid
  * removes header files for OpenGL, VDPAU, CUDA and OpenCL
- obsoletes nvidia-no_locked_io.patch
- adjusted conftest.sh.diff, conftest.sh.diff.xen-11.1-i586
* Wed Sep  8 2010 sndirsch@suse.de
- nvidia-no_locked_io.patch
  * fixed build on kernel 2.6.36
- removed obsolete and no longer applied buildfix.diff
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
    running two or more VDPAU applications simultaneously.
* Thu Aug 12 2010 boris@steki.net
- added fetch.sh and automatic version finding from .spec file
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
* Wed Jul 21 2010 sndirsch@suse.de
- update to 256.35
  * specfile adjustments done by Vitaliy Tomin; thanks a lot!
* Sat Jun 12 2010 sndirsch@suse.de
- update to 195.36.31
  * Fixed a problem with SLI SFR, AFR, and SLIAA modes with GeForce
    GTX 480 and GeForce GTX 470 and high-resolution display modes.
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
* Wed Apr  7 2010 sndirsch@suse.de
- added 0x0a2c/0x0a7c as supported also for kernel module
  (bnc #587998)
* Thu Mar 18 2010 sndirsch@suse.de
- fixed build on Xen for SLE11/11.1
* Thu Mar 18 2010 sndirsch@suse.de
- update to 195.36.15
- obsoletes conftest.sh.diff-2.6.33,
  nvacpi-acpi_walk_namespace-2.6.33
- new: /etc/OpenCL/vendors/, /usr/include/CL
- added 0x0a2c/0x0a7c as supported (missing in documentation)
* Wed Mar 17 2010 sndirsch@suse.de
- fixed build on kernel 2.6.33
* Mon Jan 11 2010 sndirsch@suse.de
- reenabled build on 2.6.27 Xen kernels (bnc #569565)
* Fri Dec 18 2009 sndirsch@suse.de
- update to 190.53
* Fri Dec  4 2009 sndirsch@suse.de
- blacklist nouveau driver
* Tue Nov 24 2009 ro@suse.de
- add macro kver for kernel version
- use macro kver to find which patches to apply
- do not build xen flavor for 2.6.32
* Fri Oct 30 2009 sndirsch@suse.de
- update to 190.42
- disabled xen flavor on openSUSE > 11.1. since it requires (now?)
  GPL-only symbol 'xen_features'
* Sat Aug 22 2009 sndirsch@suse.de
- update to 185.18.36
  * Fixed a bug that caused kernel panics when starting X on some
    mobile GPUs.
  * fixed various VDPAU issues
* Fri Aug  7 2009 ro@suse.de
- update to 185.18.31
* Sat Jul  4 2009 sndirsch@suse.de
- cleanup
* Sat Jun 20 2009 sndirsch@suse.de
- no longer hardcode supplements in driver (bnc #514394)
* Wed Jun 10 2009 sndirsch@suse.de
- conftest.sh.diff.xen-11.0
  * fixes build on xen kernels for 11.0
* Tue Jun  9 2009 ro@suse.de
- kernel-module-package options are not identical on all releases
* Mon Jun  8 2009 sndirsch@suse.de
- conftest.sh.diff.xen-11.1-i586
  * fixes build on 11.1-i586 for xen kernels
* Sat Jun  6 2009 sndirsch@suse.de
- release 185.14.18
  * removed support for GeForce 6800, GeForce 6800 LE,
    GeForce 6800 GT, GeForce 6800 XT (0x0211, 0x0212, 0x0215, 0x0218)
  * added support for GeForce 9300 / nForce 730i (0x086C)
  * various fixes
* Fri Jun  5 2009 sndirsch@suse.de
- specfile cleanup
* Tue May 26 2009 ro@suse.de
- make it build even without uname hack
  use SYSSRC and SYSOUT variables
* Thu May  7 2009 ro@suse.de
- fix typo in last change
* Mon May  4 2009 ro@suse.de
- reference patches in specfile via macro names
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
* Fri Feb 27 2009 sndirsch@suse.de
- added secret/undocumented 9500 GS (10de:0644) as supported to the
  list of supported cards (Harald Müller-Ney <hmuelle@suse.de>)
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
* Wed Jan 21 2009 sndirsch@suse.de
- readded accidently removed GeForce 9400 GT (10de:0641) to list
  of supported cards (bnc #467910)
* Fri Jan 16 2009 sndirsch@suse.de
- added Quadro FX 3700M (10de:061E) to list of supported chips
  (bnc #466892)
* Tue Jan 13 2009 sndirsch@suse.de
- replaced disabled Xen patches with an updated one and enabled
  it; reenabled build of xen kernels (bnc #465176)
* Sun Jan 11 2009 ro@suse.de
- remove hardcoded files argument
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
* Mon Nov  3 2008 sndirsch@suse.de
- removed unfunctional uame hack
* Thu Oct 30 2008 sndirsch@suse.de
- added GeForce 9400 GT (10de:0641) to list of supported cards
  (bnc #433171)
* Fri Oct 17 2008 olh@suse.de
- add ExclusiveArch x86 x86_64
* Tue Oct  7 2008 sndirsch@suse.de
- release 177.80
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
