# Important  
If you are using kernel 6.6 or higher add the kernel parameter ``nvidia_drm.modeset=1`` otherwise xorg does not start giving segmentation fault  

Here it's very simple, just run ``makepkg -si`` in "ALMOST" all folders  
NOTE: There are two folders, one is nvidia-304xx and the other is nvidia-304xx-lts  
nvidia-304xx-lts is only if you are using kernel-lts  

It is also necessary to downgrade the xf86-input-libinput package in version 1.1.0 otherwise the keyboard and mouse did not work you can download here:  
https://archive.archlinux.org/packages/x/xf86-input-libinput/xf86-input-libinput-1.1.0-1-x86_64.pkg.tar.zst  
Uncomment the IgnorePkg line in the /etc/pacman.conf file and add xf86-input-libinput  
like this IgnorePkg = xf86-input-libinput  
you can do this also using this command  
``sudo sed -i 's/#IgnorePkg   =/IgnorePkg = xf86-input-libinput/g' /etc/pacman.conf``  
