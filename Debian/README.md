# NOTE
If you already have all the necessary packages click here for the next step

## To build nvidia-graphics-driver
You may be compiling this package using Debian 10/11/12
I recommend compiling using Debian 10 for the sake of compatibility between versions (11,12,sid)

Run the command ```dpkg-buildpackage -b -us -uc```
Run the command to build for i386 ```dpkg-buildpackage -b -us -uc -ai386```

If dependencies are missing, you can install them manually or use the command below (NOTE: only work for amd64 build)
```
apt-get install     --yes $(dpkg-checkbuilddeps 2>&1 | sed -e 's/dpkg-checkbuilddeps:\serror:\sUnmet build dependencies: //g' -e  's/[\(][^)]*[\)] //g')
```

Packages required to install on amd64
- libgl1-nvidia-legacy-304xx-glx_304.137-18_amd64.deb
- libgl1-nvidia-legacy-304xx-glx_304.137-18_i386.deb
- libnvidia-legacy-304xx-cfg1_304.137-18_amd64.deb
- libnvidia-legacy-304xx-cfg1_304.137-18_i386.deb
- libnvidia-legacy-304xx-glcore_304.137-18_amd64.deb
- libnvidia-legacy-304xx-glcore_304.137-18_i386.deb
- libnvidia-legacy-304xx-ml1_304.137-18_amd64.deb
- nvidia-legacy-304xx-alternative_304.137-18_amd64.deb
- nvidia-legacy-304xx-driver_304.137-18_amd64.deb
- nvidia-legacy-304xx-driver-bin_304.137-18_amd64.deb
- nvidia-legacy-304xx-driver-libs_304.137-18_amd64.deb
- nvidia-legacy-304xx-driver-libs_304.137-18_i386.deb
- nvidia-legacy-304xx-driver-libs-i386_304.137-18_i386.deb
- nvidia-legacy-304xx-kernel-dkms_304.137-18_amd64.deb
- nvidia-legacy-304xx-kernel-support_304.137-18_amd64.deb
- nvidia-legacy-304xx-vdpau-driver_304.137-18_amd64.deb
- nvidia-settings-legacy-304xx_304.137-3_amd64.deb
- xserver-xorg-video-nvidia-legacy-304xx_304.137-18_amd64.deb

i386
- libgl1-nvidia-legacy-304xx-glx_304.137-18_i386.deb
- libnvidia-legacy-304xx-cfg1_304.137-18_i386.deb
- libnvidia-legacy-304xx-glcore_304.137-18_i386.deb
- libnvidia-legacy-304xx-ml1_304.137-18_i386.deb
- nvidia-legacy-304xx-alternative_304.137-18_i386.deb
- nvidia-legacy-304xx-driver_304.137-18_i386.deb
- nvidia-legacy-304xx-driver-bin_304.137-18_i386.deb
- nvidia-legacy-304xx-driver-libs_304.137-18_i386.deb
- nvidia-legacy-304xx-kernel-dkms_304.137-18_i386.deb
- nvidia-legacy-304xx-kernel-support_304.137-18_i386.deb
- nvidia-legacy-304xx-vdpau-driver_304.137-18_i386.deb
- nvidia-settings-legacy-304xx_304.137-3_i386.deb
- xserver-xorg-video-nvidia-legacy-304xx_304.137-18_i386.deb

If you are using Debian 12 you need to download these packages
https://archive.debian.org/debian/pool/main/n/
https://archive.debian.org/debian/pool/contrib/n/
- nvidia-xconfig_470.103.01-1~deb11u1_amd64.deb
- nvidia-kernel-common_20151021+13_amd64.deb

## To build nvidia-settings
You may be compiling this package using Debian 10/11/12
I recommend compiling using Debian 10 for the sake of compatibility between versions (11,12,sid)

Run the command ```dpkg-buildpackage -b -us -uc```
Run the command to build for i386 ```DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -b -us -uc -ai386```

If dependencies are missing, you can install them manually or use the command below (NOTE: only work for amd64 build)
```
apt-get install     --yes $(dpkg-checkbuilddeps 2>&1 | sed -e 's/dpkg-checkbuilddeps:\serror:\sUnmet build dependencies: //g' -e  's/[\(][^)]*[\)] //g')
```

## To build xorg-server
This package was built using Debian 9 you may be using a virtual (or real) machine to compile or you may be using a jail
to create a Debian 9 jail is very simple
first install debootstrap on your distribution
After that, run the commands below to create the jail on their respective architectures (**amd64, i386**)

**(amd64)**
```
sudo debootstrap stretch /jaula-stretch https://archive.debian.org/debian
```
**(i386)**
```
sudo debootstrap --arch=i386 stretch /jaula-stretch-32 https://archive.debian.org/debian
```

The jails containing debian 9 will be created in the **/jaula-stretch** and **/jaula-stretch-32** folders respectively
to enter, run the command
```
chmod /jaula-stretch
```
or
```
chmod /jaula-stretch-32
```

Now that we are inside, run the following commands
```
echo proc /proc proc defaults 0 0 >> /etc/fstab
mount /proc
apt update
apt install debian-archive-keyring
apt install nano
apt update ; apt full-upgrade
```

Now add these lines at the end of /etc/bash.bashrc file "nano /etc/bash.bashrc"
```
export LANG=C.UTF-8
export LANGUAGE=C.UTF-8
export LC_ALL=C.UTF-8
export PS1='JAULA-STRETCH-\u@\h:\w\$ '
mount /proc
```
Then run  ```source /etc/bash.bashrc```

Now we install some packages necessary to compile xorg package
```apt install build-essential devscripts dh-make```

Now clone this repository and go to the debian/xorg-server folder
and run the command ```dpkg-buildpackage -b -us -uc```
If dependencies are missing, you can install them manually or use the command below
```
apt-get install     --yes $(dpkg-checkbuilddeps 2>&1 | sed -e 's/dpkg-checkbuilddeps:\serror:\sUnmet build dependencies: //g' -e  's/[\(][^)]*[\)] //g')
```

After the compilation is finished you will only need the xserver-xorg-core package
xserver-xorg-core_1.19.2-1+deb9u10_amd64.deb

and you can be installing with this command here
```sudo apt install ./*.deb -y --allow-downgrades ```

However, if you installed the graphical environment using tasksel when trying to downgrade xorg, not only the graphical environment will be removed, but also other important packages
To avoid this, we just need to downgrade some extra packages alongside the packages we just compiled.
download them from the link below
https://archive.debian.org/debian/pool/main/x/
https://archive.debian.org/debian/pool/main/libx/

The required packages are:

- libxcb-util0_0.3.8-3+b2_amd64.deb
- xserver-xorg-video-amdgpu_1.2.0-1+b1_amd64.deb
- xserver-xorg-video-ati_7.8.0-1+b1_amd64.deb
- xserver-xorg-video-fbdev_0.4.4-1+b5_amd64.deb
- xserver-xorg-video-intel_2.99.917+git20161206-1_amd64.deb
- xserver-xorg-video-nouveau_1.0.13-3_amd64.deb
- xserver-xorg-video-qxl_0.1.4+20161126git4d7160c-1_amd64.deb
- xserver-xorg-video-radeon_7.8.0-1+b1_amd64.deb
- xserver-xorg-video-vesa_2.3.4-1+b2_amd64.deb
- xserver-xorg-video-vmware_13.2.1-1+b1_amd64.deb

And if you are using Debian 12 it is also necessary:
- xserver-xorg-input-libinput_1.1.0-1_amd64.deb
- xserver-xorg-input-wacom_0.34.0-1_amd64.deb

After that, run the command again (NOTE: the .deb files must all be in the same folder)
```sudo apt install ./*.deb -y --allow-downgrades ```


Now prevents the updating of packages that we downgraded with the command below
```sudo apt-mark hold xserver-xorg-core```

With xorg in version 1.19 we can now install the nvidia 304.137 driver

