# nvidia-304
This repository contains fixed packages and patches to use the Nvidia 304.137 driver on newer Linux distros (up to kernel 6.12)

Inside each distribution folder you will find tutorials for generating the packages and installing the driver
## Supported Desktop environment
You can use any desktop environment that hasn't made too drastic changes over the years  
I can mention some like XFCE, LXDE, LXQT, MATE (should work), JWM, OpenBox and others. Forget Gnome and its forks that use mutter, it won't work well here and KDE can work with some workarounds, but it's not the most suitable   
## Supported distros
**Debian**
- 12/13?/Sid(**tested on unstable 2024/07/02**)  

**Ubuntu**
- 22.04/24.04  

**Mageia**
- 9?  

**Archlinux/Manjaro**
- Archlinux using linux(6.9) and linux-lts(6.6)
- Manjaro all kernel variants 4.19/5.4/5.10/6.1/6.6/6.9/6.10  

**Opensuse**
- Leap 15.4/15.5/15.6?
- Tumbleweed?  

**Fedora**
- 39/40/41  

## Issues
### **XFCE or XFWM4 showing black screen with cursor only:**  
Run the command below or disable the window composer before installing the driver  
```xfconf-query -c xfwm4 -p /general/vblank_mode -s xpresent```  
If the above command fails, run this  
```xfconf-query -c xfwm4 -p /general/vblank_mode -t string -s "xpresent" --create```  

### **I can't use the driver on Debian 32 bits the installation fails:**  
Most likely you need to compile a kernel with **LKDTM(CONFIG_LKDTM)** enabled

### **Firefox crashes for no apparent reason:**  
Go to **about:config** and change the **webgl.disabled** parameter to true  

### **Resolution locked at 960x540:**  
Comment out or delete the **HorizSync** and **VertRefresh** lines in xorg.conf  
```
sudo sed -i 's/HorizSync/#HorizSync/' /etc/X11/xorg.conf
sudo sed -i 's/VertRefresh/#VertRefresh/' /etc/X11/xorg.conf
```

### **Xorg segfault:**  
> If I'm not mistaken, this parameter is necessary since kernel version 5.17/5.18

Add **nvidia_drm.modeset=1** and **initcall_blacklist=simpledrm_platform_driver_init** as kernel parameter  

### **LightDM does not start or black screen:**  
Add **logind-check-graphical=false** in **/etc/lightdm/lightdm.conf**  
```
[LightDM]
logind-check-graphical=false
```
or use the command below
```
sudo sed -i 's/\[LightDM\]/[LightDM]\nlogind-check-graphical=false/' /etc/lightdm/lightdm.conf
```
  
### **Chromium-based browsers and electron apps do not work properly:**    
Start the application with the --disable-gpu parameter and that should fix it    
Depending on the distribution and application you are using, you can leave these flags permanent.  
In Archlinux, you can follow this link below and adapt it to your use:  
https://wiki.archlinux.org/title/Chromium#Making_flags_persistent  
  
Some flatpak applications also have this feature, I'll give Chrome as an example.  
```
#Chrome flatpak
echo -e "--disable-gpu" >> ~/.var/app/com.google.Chrome/config/chrome-flags.conf
```  
In ArchLinux for electron based applications you can use the link below and adapt it for your use.  
https://wiki.archlinux.org/title/Wayland#Command_line_flags  


### **KDE Plasma 6 Workaround (tested on Archlinux):**  
Add the **libGL.so.1** library to the **libQt6Gui.so.6** using patchelf  
```sudo patchelf --add-needed /usr/lib/nvidia/libGL.so.1 /usr/lib/libQt6Gui.so.6```  
  
Add this in **.config/kdeglobals**  
```
[QtQuickRendererSettings]
RenderLoop=basic
SceneGraphBackend=opengl
```  
Put this in **/etc/environment**  
```
KWIN_EXPLICIT_SYNC=0
__GL_YIELD=USLEEP
__GL_FSAA_MODE=0
__GL_LOG_MAX_ANISO=0
KWIN_OPENGL_INTERFACE=glx
KWIN_NO_GL_BUFFER_AGE=1
```

**For arch-based distros only**  
You can create a hook with these parameters so whenever the qt6-base package is updated it will always receive nvidia libGL.so.1  
```
[Trigger]
Operation=Install
Operation=Upgrade
Type=Package
Target=qt6-base

[Action]
Description=Patching Nvidia libGL in libQt6Gui.so.6
Depends=patchelf
When=PostTransaction
Exec=/usr/bin/patchelf --add-needed /usr/lib/nvidia/libGL.so.1 /usr/lib/libQt6Gui.so.6
```  
Add the content in **/etc/pacman.d/hooks/** to a file with the **.hook** extension, example: **novideo.hook**  
Also don't forget to uncomment the HookDir line in the pacman.conf file  

### **Applications giving segmentation fault, black screen or not recognizing the driver:**  
Try starting them with the LD_PRELOAD parameter pointing to the driver's libGL.so.*  
Example in ubuntu:  
```
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGL.so.304.137 PPSSPPSDL
```

### **Flatpak Fix:**  
It may be necessary to load libGL.so.304.137 along with the program for it to work. For this, you can pass the **--env** argument next to the **flatpak run** command  
Example of a 64-bit application:  
```
flatpak run --env=LD_PRELOAD=/usr/lib/x86_64-linux-gnu/GL/nvidia-304-137/lib/libGL.so.304.137 org.ppsspp.PPSSPP
```  
Or apply the variable globally across all flatpaks by creating the global file at ~/.local/share/flatpak/overrides  
```
#If the directory does not exist, it is good to create it
mkdir -p ~/.local/share/flatpak/overrides
echo -e "[Environment]\nLD_PRELOAD=/usr/lib/x86_64-linux-gnu/GL/nvidia-304-137/lib/libGL.so.304.137:/app/lib/i386-linux-gnu/GL/nvidia-304-137/lib/libGL.so.304.137" >> ~/.local/share/flatpak/overrides/global
```  
  
### **Segmentation faults when opening QT5 applications or crashes when starting the graphical environment:**  
If when you click on QT5 applications and nothing happens or the graphical environment does not want to start, check the system logs by running ``dmesg``  
```
[ 827.938059] konsole[3683]: segfault at 0 ip 0000000000000000 sp 00007ffcd745b928 error 14 in konsole[55b9167e0000+4000]  
[ 827.938072] Code: Unable to access opcode bytes at RIP 0xffffffffffffffd6.
```
If you see lines similar to this, run the command below  
  
**Mageia:**
```
sudo patchelf --add-needed /usr/lib64/libpthread.so.0 /usr/lib64/nvidia304/libGL.so.1
```  
**Opensuse:**
```
sudo patchelf --add-needed /lib64/libpthread.so.0 /usr/X11R6/lib64/libGL.so.304.137
```  

