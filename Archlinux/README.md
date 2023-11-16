# It is currently not working on kernel 6.6
The only thing different is that in kernel 6.6 this warning appears on dkms make.log and xorg does not start giving segmentation fault.  
6.5 works fine.  
```/var/lib/dkms/nvidia/304.137/build/nvidia.o: warning: objtool: _nv000252rm+0x73: unannotated intra-function call```  

Here it's very simple, just run ``makepkg -si`` in "ALMOST" all folders  
NOTE: There are two folders, one is nvidia-304xx and the other is nvidia-304xx-lts  
nvidia-304xx-lts and only if you are using kernel-lts  

It is also necessary to downgrade the xf86-input-libinput package in version 1.1.0 otherwise the keyboard and mouse did not work you can download here:  
https://archive.archlinux.org/packages/x/xf86-input-libinput/xf86-input-libinput-1.1.0-1-x86_64.pkg.tar.zst  
Uncomment the IgnorePkg line in the /etc/pacman.conf file and add xf86-input-libinput  
like this IgnorePkg = xf86-input-libinput  
you can do this also using this command  
``sudo sed -i 's/#IgnorePkg   =/IgnorePkg = xf86-input-libinput/g' /etc/pacman.conf``  
