# nvidia-304
This repository contains fixed packages and patches to use the Nvidia 304.137 driver on newer Linux distros (up to kernel 6.8)

Inside each distribution folder you will find tutorials for generating the packages and installing the driver
## Supported distros
**Debian**
- 10/11/12/Sid  

**Ubuntu**
- 20.04/22.04/23.04/23.10  

**Mageia**
- 9  

**Archlinux/Manjaro**
- Archlinux using linux(6.8) and linux-lts(6.1)
- Manjaro all kernel variants 4.19/5.4/5.10/6.1/6.5/6.6/6.8  

**Opensuse**
- Leap 15.4/15.5
- Tumbleweed  

**Fedora**
- 39  

## Issues
**XFCE or XFWM4 showing black screen with cursor only:**  
Run the command below or disable the window composer before installing the driver  
```xfconf-query -c xfwm4 -p /general/vblank_mode -s xpresent```  
If the above command fails, run this  
```xfconf-query -c xfwm4 -p /general/vblank_mode -t string -s "xpresent" --create```  

**I can't use the driver on Debian 32 bits the installation fails:**  
Most likely you need to compile a kernel with **LKDTM(CONFIG_LKDTM)** enabled

**Firefox crashes for no apparent reason:**  
Go to **about:config** and change the **webgl.disabled** parameter to true  

**Resolution locked at 960x540:**  
Comment out or delete the **HorizSync** and **VertRefresh** lines in xorg.conf  

**Xorg segfault:**  
Add **nvidia_drm.modeset=1** as kernel parameter  

**LightDM does not start:**  
Add **logind-check-graphical=false** in **/etc/lightdm/lightdm.conf**  
```
[LightDM]
logind-check-graphical=false
```  

**Segmentation faults when opening QT5 applications or crashes when starting the graphical environment:**  
If when you click on QT5 applications and nothing happens or the graphical environment does not want to start, check the system logs by running ``dmesg``  
```
[ 827.938059] konsole[3683]: segfault at 0 ip 0000000000000000 sp 00007ffcd745b928 error 14 in konsole[55b9167e0000+4000]  
[ 827.938072] Code: Unable to access opcode bytes at RIP 0xffffffffffffffd6.
```
If you see lines similar to this, run the command below

**Debian amd64:**
```
sudo patchelf --add-needed /usr/lib/x86_64-linux-gnu/libpthread.so.0 /etc/alternatives/glx--libGL.so.1-x86_64-linux-gnu
```  
**Debian i386:**
```
sudo patchelf --add-needed /usr/lib/i386-linux-gnu/libpthread.so.0 /etc/alternatives/glx--libGL.so.1-i386-linux-gnu
```  
**Ubuntu:**
```
sudo patchelf --add-needed /usr/lib/x86_64-linux-gnu/libpthread.so.0 /usr/lib/x86_64-linux-gnu/libGL.so.304.137
```  
**Mageia:**
```
sudo patchelf --add-needed /usr/lib64/libpthread.so.0 /usr/lib64/nvidia304/libGL.so.1
```  
**Archlinux/Manjaro:**
```
sudo patchelf --add-needed /usr/lib64/libpthread.so.0 /usr/lib/nvidia/libGL.so.304.137
```  
**Opensuse:**
```
sudo patchelf --add-needed /lib64/libpthread.so.0 /usr/X11R6/lib64/libGL.so.304.137
```
**Fedora:**  
```
sudo patchelf --add-needed /lib64/libpthread.so.0 /usr/lib64/nvidia-304xx/libGL.so.304.137
```  

