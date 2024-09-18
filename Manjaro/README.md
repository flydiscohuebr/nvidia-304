# Important  
If you are using kernel 6.6 or higher add the kernel parameter ``nvidia_drm.modeset=1`` and ``initcall_blacklist=simpledrm_platform_driver_init`` otherwise xorg does not start giving segmentation fault  

Here it's very simple, just run ``makepkg -si`` in all folders

It is also necessary to downgrade the xf86-input-libinput package in version 1.1.0 otherwise the keyboard and mouse did not work you can download here:  
https://archive.archlinux.org/packages/x/xf86-input-libinput/xf86-input-libinput-1.1.0-1-x86_64.pkg.tar.zst  
Uncomment the IgnorePkg line in the /etc/pacman.conf file and add xf86-input-libinput  
like this IgnorePkg = xf86-input-libinput  
you can do this also using this command  
``sudo sed -i 's/#IgnorePkg   =/IgnorePkg = xf86-input-libinput/g' /etc/pacman.conf``  

