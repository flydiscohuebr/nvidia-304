Copy and paste the rpmbuild folder into your user's home folder

now install rpmbuild  
```sudo zypper in rpmbuild rpmdevtools```  

run the install-deps.sh script it will install the packages needed to build the packages  
```sudo bash install-deps.sh```  

Navigate to the rpmbuild/SPECS folder  
```cd ~/rpmbuild/SPECS```  

Now run the command below  
```rpmbuild -ba xorg-x11-server.spec```  

Run this command to remove a conflicting package  
```sudo rpm -e --nodeps xorg-x11-server-Xvfb```  

First we downgrade the xorg-x11-server-sdk package  
```
cd ~/rpmbuild/RPMS/x86_64
sudo zypper in --oldpackage --allow-unsigned-rpm --no-confirm ./xorg-x11-server-sdk*
```  

Now let's build and install the remaining packages, so run the commands below  
```
cd ~/rpmbuild/SPECS
rpmdev-spectool -g x11-video-nvidiaG02.spec ; mv *.run ../SOURCES
rpmbuild -ba xf86-input-libinput.spec
rpmbuild -ba dkms-nvidia.spec
rpmbuild -ba x11-video-nvidiaG02.spec
cd ~/rpmbuild/RPMS/x86_64
sudo zypper in --oldpackage --allow-unsigned-rpm --no-confirm --force-resolution ./xorg-x11-server-1.19.7* ./xorg-x11-server-extra* ./xf86-input-libinput-1*
sudo zypper in --allow-unsigned-rpm --no-confirm ./dkms*
sudo zypper in --allow-unsigned-rpm --no-confirm ./nvidia*
sudo zypper in --allow-unsigned-rpm --no-confirm ./x11-video*
```  

Add nouveau to blacklist  
```
sudo bash -c "echo blacklist nouveau > /etc/modprobe.d/blacklist-nvidia-nouveau.conf"
sudo bash -c "echo options nouveau modeset=0 >> /etc/modprobe.d/blacklist-nvidia-nouveau.conf"
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& rd.driver.blacklist=nouveau/' /etc/default/grub
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& nomodeset/' /etc/default/grub
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
sudo dracut -f --regenerate-all
sudo update-bootloader --refresh
```

If you are using tumbleweed, this is also necessary  
```
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*/& nvidia_drm.modeset=1/' /etc/default/grub
```  

Reinstall libvdpau1  
```sudo zypper install -f libvdpau1``` 

If everything went well, we have the driver installed.  
Now just run the command ```sudo nvidia-xconfig --no-logo``` and restart the machine  
