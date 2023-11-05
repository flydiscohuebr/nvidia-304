Enter the folder nvidia-graphics-drivers and run the command ```dpkg-buildpackage -b -us -uc```  

If dependencies are missing, you can install them manually or use the command below
```apt-get install     --yes $(dpkg-checkbuilddeps 2>&1 | sed -e 's/dpkg-checkbuilddeps:\serror:\sUnmet build dependencies: //g' -e  's/[\(][^)]*[\)] *//g')```  

You can download xorg 1.19 here
http://archive.ubuntu.com/ubuntu/pool/main/x/xorg-server/xserver-xorg-core_1.19.6-1ubuntu4.15_amd64.deb
SHA512:341febec443450fd37e20cc82f7c4ad14dc66bf0370e3344773d19ff9036ad18063713c93f68390ce11a048c4e3d6a65690a5ad756f6aebb376b7d3b27e49610
http://archive.ubuntu.com/ubuntu/pool/main/x/xserver-xorg-input-libinput/xserver-xorg-input-libinput_0.29.0-1_amd64.deb
SHA512:72627285ed5016b984d4b2eea07db266315fc912e963c149d43bea4fa0acff35dffb32ba02edd13618a640058a8c330dd64cf44667c16a51a4110b12f9968b7e

Downgrade and hold xorg updates (be careful this may remove some important packages)
```
sudo apt install ./xserver-xorg-core_1.19.6-1ubuntu4.15_amd64.deb --allow-downgrades
sudo apt install ./xserver-xorg-input-libinput_0.29.0-1_amd64.deb
sudo apt-mark hold xserver-xorg-core xserver-xorg-input-libinput
```  

Install the generated packages from nvidia-graphics-drivers  
```sudo apt install ../nvidia-304_*.deb```  

At some point I ended up breaking something and now the file that put nouveau on the blacklist is no longer created XD
So for now just run this command here (I'll fix it later)
``` echo -e "blacklist nouveau\nblacklist lbm-nouveau\noptions nouveau modeset=0\nalias nouveau off\nalias lbm-nouveau off" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf > /dev/null ```

Run the commands below  
```
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/nvidia-304/xorg\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/xorg/modules\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i 's/HorizSync/#HorizSync/' /etc/X11/xorg.conf
sudo sed -i 's/VertRefresh/#VertRefresh/' /etc/X11/xorg.conf
```  
Run the command sudo ```nvidia-xconfig --no-logo``` and restart the computer  

