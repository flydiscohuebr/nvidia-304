## nvidia-graphics-driver 
Run the command below inside the nvidia-graphics-drivers304 folder.

```dpkg-buildpackage -b -us -uc```

If dependencies are missing, you can install them manually or use the command below
```
sudo apt build-dep .
```  

If you get the error ```sh: 0: cannot open amd64/NVIDIA-Linux-x86_64-304.137.run: No such file```, run the commands below  
```
dpkg-buildpackage -T get-orig-source
tar -xvzf nvidia-graphics-drivers-legacy-304xx_304.137.orig-amd64.tar.gz
tar -xvzf nvidia-graphics-drivers-legacy-304xx_304.137.orig-i386.tar.gz
mv nvidia-graphics-drivers-304.137.orig-amd64 amd64
mv nvidia-graphics-drivers-304.137.orig-i386 i386
```  

Packages required to install on:  
amd64

- nvidia-legacy-304xx-driver
- nvidia-legacy-304xx-driver-libs
- nvidia-legacy-304xx-driver-bin
- xserver-xorg-video-nvidia-legacy-304xx
- nvidia-legacy-304xx-vdpau-driver
- nvidia-legacy-304xx-alternative
- nvidia-legacy-304xx-kernel-dkms
- libnvidia-legacy-304xx-ml1
- libgl1-nvidia-legacy-304xx-glx
- libnvidia-legacy-304xx-cfg1
- nvidia-legacy-304xx-kernel-support
- libnvidia-legacy-304xx-glcore


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

## nvidia-settings
Run the command below inside the nvidia-settings folder.

 ```dpkg-buildpackage -b -us -uc```  

If dependencies are missing, you can install them manually or use the command below
```
sudo apt build-dep .
```  

## xorg-server
Run the command below inside the xorg-server folder

```dpkg-buildpackage -b -us -uc```  

If dependencies are missing, you can install them manually or use the command below
```
sudo apt build-dep .
```  

After the compilation is finished you will only need the xserver-xorg-core package  
xserver-xorg-core_*.deb

and you can be installing with this command here  
```sudo apt install ./xserver-xorg-core_*.deb --allow-downgrades ```

**Attention**  
It is necessary to downgrade the xserver-xorg-input-libinput package; otherwise, you may lose access to the keyboard and mouse in graphical mode.  
You can download a compatible version using the link below.  

https://snapshot.debian.org/archive/debian/20210825T144238Z/pool/main/x/xserver-xorg-input-libinput/xserver-xorg-input-libinput_1.1.0-1_amd64.deb

If you already have a desktop environment installed, be careful because running this command may mark some packages for removal.  
I recommend listing them and reinstalling if necessary.  

Now prevents the updating of packages that we downgraded with the command below  
```sudo apt-mark hold xserver-xorg-core```

With Xorg in version 1.19 we can now install the Nvidia 304.137 driver  
To install the Nvidia 304.137 driver, take the packages mentioned above, place them in a folder and run the command below  
```sudo apt install ./*.deb --allow-downgrades ```  

Now run the commands below to prevent packages from being updated  

amd64
```
sudo apt-mark hold \
libgl1-nvidia-legacy-304xx-glx \
libnvidia-legacy-304xx-cfg1 \
libnvidia-legacy-304xx-glcore \
libnvidia-legacy-304xx-ml1 \
nvidia-legacy-304xx-alternative \
nvidia-legacy-304xx-driver \
nvidia-legacy-304xx-driver-bin \
nvidia-legacy-304xx-driver-libs \
nvidia-legacy-304xx-kernel-dkms \
nvidia-legacy-304xx-kernel-support \
nvidia-legacy-304xx-vdpau-driver \
nvidia-settings-legacy-304xx \
xserver-xorg-video-nvidia-legacy-304xx
```
i386
```
sudo apt-mark hold \
libgl1-nvidia-legacy-304xx-glx \
libgl1-nvidia-legacy-304xx-glx:i386 \
libnvidia-legacy-304xx-cfg1 \
libnvidia-legacy-304xx-cfg1:i386 \
libnvidia-legacy-304xx-glcore \
libnvidia-legacy-304xx-ml1 \
nvidia-legacy-304xx-alternative \
nvidia-legacy-304xx-driver \
nvidia-legacy-304xx-driver-bin \
nvidia-legacy-304xx-driver-libs \
nvidia-legacy-304xx-driver-libs:i386 \
nvidia-legacy-304xx-kernel-dkms \
nvidia-legacy-304xx-kernel-support \
nvidia-legacy-304xx-vdpau-driver \
nvidia-settings-legacy-304xx \
xserver-xorg-video-nvidia-legacy-304xx
```

Just run ```sudo nvidia-xconfig --no-logo``` and restart your computer
