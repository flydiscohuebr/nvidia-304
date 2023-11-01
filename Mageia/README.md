# Build
ONLY TESTED ON X86_64 amd64
I did my installation of mageia with the development box checked, so packages like rpmbuild were already installed
To install rpmbuild, run the command as root  
``urpmi rpm-build``  
Maybe task-c-devel is necessary?

Copy the rpmbuild folder to your user's home folder
and run the commands  
```
cd ~/rpmbuild/SPECS
su -c 'urpmi nvidia304.spec'
su -c 'urpmi x11-server.spec'
```  

This will install the necessary dependencies
Now build the packages  

```
cd ~/rpmbuild/SPECS
rpmbuild -ba nvidia304.spec
rpmbuild -ba x11-server.spec
```  

After compiling the packages you will only need:
- dkms-nvidia304-304.137-3.mga9.x86_64.rpm  
- nvidia304-cuda-opencl-304.137-3.mga9.x86_64.rpm  
- x11-driver-video-nvidia304-304.137-3.mga9.x86_64.rpm  
- x11-server-1.19.6-5.mga9.x86_64.rpm  
- x11-server-common-1.19.6-5.mga9.x86_64.rpm  
- x11-server-xnest-1.19.6-5.mga9.x86_64.rpm  
- x11-server-xorg-1.19.6-5.mga9.x86_64.rpm  
- x11-server-xvfb-1.19.6-5.mga9.x86_64.rpm

The x11-driver-input-libinput-0.30.0-1.mga8.x86_64.rpm package is also required and you can download it here
https://distrib-coffee.ipsl.jussieu.fr/pub/linux/Mageia/distrib/8/x86_64/media/core/release/x11-driver-input-libinput-0.30.0-1.mga8.x86_64.rpm

# Installation

Remove x11-driver-video package along with orphan packages  
```urpme x11-driver-video ; urpme --auto-orphans```  

Downgrading xorg and installing the related packages  
```
sudo dnf downgrade --allowerasing x11-server-*.rpm x11-driver-input-libinput-0.30.0-1.mga8.x86_64.rpm
sudo dnf install x11-server-*.rpm
```  

Make the x11-driver-input-libinput and x11-server-common packages no longer updated
```sh -c 'echo -e "x11-driver-input-libinput\nx11-server-common" >> /etc/urpmi/skip.list'```  

Driver-related packages
```urpmi dkms-nvidia304*.rpm nvidia304-cuda*.rpm x11-driver-video-nvidia304*.rpm```  

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
