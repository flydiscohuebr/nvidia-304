# Important  
If xorg does not start after restarting and the logs show a segmentation fault, you need the kernel parameters described here  
[nvidia-304: xorg-segfault](https://github.com/flydiscohuebr/nvidia-304#xorg-segfault)

Here it's very simple, just run ``makepkg -si`` in all folders

It is also necessary to downgrade the xf86-input-libinput package to version 1.1.0 otherwise, the keyboard and mouse did not work. You can download here.  
https://archive.archlinux.org/packages/x/xf86-input-libinput/xf86-input-libinput-1.1.0-1-x86_64.pkg.tar.zst  
Uncomment the IgnorePkg line in the /etc/pacman.conf file and add xf86-input-libinput  
```
IgnorePkg = xf86-input-libinput
```
you can do this also using this command  
```
sudo sed -i 's/#IgnorePkg   =/IgnorePkg = xf86-input-libinput/g' /etc/pacman.conf
```

