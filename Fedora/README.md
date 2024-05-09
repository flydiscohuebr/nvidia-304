Install needed packages  
```
sudo dnf install rpm-build rpm-devel rpmdevtools
```

Copy rpmbuild folder to your home directory  

Inside the rpmbuild run the nvidia-kmod-data-generate.sh script  
```
./nvidia-kmod-data-generate.sh
```

Enable rpmfusion repo  
https://docs.fedoraproject.org/en-US/quick-docs/rpmfusion-setup/  
```
sudo dnf install \
  https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```  

Go to the rpmbuild/SPECS folder and run this command for install every dependency needed  
```
sudo dnf builddep *.spec
```  

Run this commands for download few missing files  

```
spectool -g xorg-x11-server.spec ; mv *.bz2 *.sh ../SOURCES
spectool -g xorg-x11-drv-nvidia-304xx.spec ; mv *.run ../SOURCES
```

Now build xorg  
```
rpmbuild -ba xorg-x11-server.spec
```

Before generate the xorg-x11-drv-libinput package you need to downgrade xorg first  
```
sudo dnf downgrade --allowerasing ../RPMS/x86_64/xorg-x11-server-Xorg-1.19.6* ../RPMS/x86_64/xorg-x11-server-common-1.19.6* ../RPMS/x86_64/xorg-x11-server-devel-1.19.6*
```

After downgrade xorg build and install the left packages  
```
rpmbuild -ba xorg-x11-drv-libinput.spec
sudo dnf downgrade --allowerasing ../RPMS/x86_64/xorg-x11-drv-libinput-1.0.1-*
rpmbuild -ba xorg-x11-drv-nvidia-304xx.spec
rpmbuild -ba nvidia-304xx-kmod.spec 
sudo dnf install ../RPMS/x86_64/akmod-nvidia-304xx* ../RPMS/x86_64/kmod-nvidia-304xx* ../RPMS/x86_64/xorg-x11-drv-nvidia-304xx-304.137* ../RPMS/x86_64/xorg-x11-drv-nvidia-304xx-libs*
```

Lock xorg related packages  
```
sudo dnf install 'dnf-command(versionlock)'
sudo dnf versionlock add xorg-x11-drv-libinput
sudo dnf versionlock add xorg-x11-server-Xorg
sudo dnf versionlock add xorg-x11-server-common
sudo dnf versionlock add xorg-x11-server-devel
```

reboot and enjoy
