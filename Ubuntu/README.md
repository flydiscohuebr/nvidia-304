﻿Enter the folder nvidia-graphics-drivers or xorg-server and run the command ```dpkg-buildpackage -b -us -uc```  

If dependencies are missing, you can install them manually or use the command below  
```
sudo apt build-dep .
```  
To download .run packages
```
dpkg-buildpackage -Tget-orig-source
```  

You can download xserver-xorg-input-libinput 1.1.0 here  
https://old-releases.ubuntu.com/ubuntu/pool/main/x/xserver-xorg-input-libinput/xserver-xorg-input-libinput_1.1.0-1_amd64.deb  
SHA512:512a81db07cfd340fdd3cf75be20c08ff6c948b5c531851bca35c10fbc1b505c0b3a5d9eab3e8d0107667089763a82e378576b64fc880387f3f242227e15a4da  

If you don't want to compile xorg, use this package  
http://archive.ubuntu.com/ubuntu/pool/main/x/xorg-server/xserver-xorg-core_1.19.6-1ubuntu4.15_amd64.deb  
SHA512:341febec443450fd37e20cc82f7c4ad14dc66bf0370e3344773d19ff9036ad18063713c93f68390ce11a048c4e3d6a65690a5ad756f6aebb376b7d3b27e49610  

Downgrade and hold xorg updates
```
sudo apt install ./xserver-xorg-input-libinput_1.1.0-1_amd64.deb
sudo apt install ./xserver-xorg-core_1.19.6-1ubuntu* --allow-downgrades
sudo apt-mark hold xserver-xorg-core xserver-xorg-input-libinput
```  

Install the generated packages from nvidia-graphics-drivers and nvidia-settings  
```
sudo apt install ../nvidia-304_*.deb
sudo apt install ../nvidia-settings*.deb
```  

Run the command ```nvidia-xconfig --no-logo``` to create xorg.conf then run the commands above 
```
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/nvidia-304/xorg\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/xorg/modules\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i 's/HorizSync/#HorizSync/' /etc/X11/xorg.conf
sudo sed -i 's/VertRefresh/#VertRefresh/' /etc/X11/xorg.conf
```  
Now restart the computer  

