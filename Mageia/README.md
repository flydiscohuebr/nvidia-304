# Build
ONLY TESTED ON X86_64 amd64
To install rpmbuild, run the command as root  
``urpmi rpm-build rpmdevtools``  

Copy the rpmbuild folder to your user's home folder
and run the commands  
```
cd ~/rpmbuild/SPECS
su -c 'urpmi nvidia304.spec'
su -c 'urpmi x11-server.spec'
su -c 'urpmi x11-driver-input-libinput.spec'
spectool -g nvidia304.spec
spectool -g x11-server.spec
spectool -g x11-driver-input-libinput.spec
mv *.run *.bz2 *.sh ../SOURCES/
```  

This will install the necessary dependencies
Now build the packages  

```
cd ~/rpmbuild/SPECS
rpmbuild -ba nvidia304.spec
rpmbuild -ba x11-server.spec
```  

# Installation

Remove x11-driver-video package along with orphan packages  
```urpme x11-driver-video ; urpme --auto-orphans```  

Install x11-server-devel  
```
cd ~/rpmbuild/RPMS/x86_64/
sudo dnf install x11-server-devel-1.19.6-5.mga9.x86_64.rpm
```  

Now build x11-driver-input-libinput  
```
cd ~/rpmbuild/SPECS
su -c 'urpmi x11-driver-input-libinput.spec'
rpmbuild -ba x11-driver-input-libinput.spec
cd ~/rpmbuild/RPMS/x86_64/
sudo dnf install x11-driver-input-libinput-1.1.0-1.mga9.x86_64.rpm
```  

Downgrading xorg and installing the related packages  
```
cd ~/rpmbuild/RPMS/x86_64/
sudo dnf install x11-server-1.19.6-5.mga9.x86_64.rpm
sudo dnf downgrade --allowerasing x11-server-1.19.6-5.mga9.x86_64.rpm x11-server-common-1.19.6-5.mga9.x86_64.rpm x11-server-xnest-1.19.6-5.mga9.x86_64.rpm x11-server-xorg-1.19.6-5.mga9.x86_64.rpm x11-server-xvfb-1.19.6-5.mga9.x86_64.rpm
```  
If you want to use dnf to update the system and it is useful to add the xorg packages in the exclusion  
add the line below in **/etc/dnf/dnf.conf**  
```exclude=x11-server x11-server-devel x11-server-common```  

Make the x11-driver-input-libinput and x11-server-common packages no longer updated  
```sh -c 'echo -e "x11-driver-input-libinput\nx11-server-common" >> /etc/urpmi/skip.list'```  

Driver-related packages (OBS: to satisfy the kernel-devel dependency use kernel-desktop-devel)  
```urpmi dkms-nvidia304*.rpm x11-driver-video-nvidia304*.rpm```  

installing the driver OBS: you can use XFdrake  
```
sudo sed -i 's/nouveau/nvidia/' /etc/X11/xorg.conf
sudo sed -i '/Module/a Load "glx"' /etc/X11/xorg.conf
sudo update-alternatives --set gl_conf /etc/nvidia304/ld.so.conf
sudo ldconfig -X
```  

Done
Now just restart and everything should be working
If the graphical environment does not start, run the command described on the home page of this repository, if this does not resolve it, check the system logs "dmesg" and the Xorg logs "/var/log/Xorg.log.0"
