Copy and paste the rpmbuild folder into your user's home folder

now install rpmbuild  
```sudo zypper in rpmbuild```  

run the test.sh script it will install the packages needed to build the packages  
```sudo bash install-deps.sh```  

Navigate to the rpmbuild/SPECS folder  
```cd ~/rpmbuild/SPECS```  

Now run the command below  
```rpmbuild -ba xorg-x11-server.spec```  

Run this command to remove a conflicting package  
```sudo rpm -e --nodeps xorg-x11-server-Xvfb```  

Now let's downgrade xorg, run the commands below  
```
cd ~/rpmbuild/RPMS/x86_64
sudo zypper in --oldpackage --allow-unsigned-rpm --no-confirm --force-resolution ./xorg-x11-server-1.19.7* ./xorg-x11-server-extra*
sudo zypper in --oldpackage --allow-unsigned-rpm --no-confirm ./xorg-x11-server-sdk*
```  

Now let's build the remaining packages, so run the commands below  
```
cd ~/rpmbuild/SPECS
rpmbuild -ba xf86-input-libinput.spec
rpmbuild -ba dkms-nvidia.spec
rpmbuild -ba x11-video-nvidiaG02.spec
cd ~/rpmbuild/RPMS/x86_64
sudo zypper in --oldpackage --allow-unsigned-rpm --no-confirm  ./packages/xf86-input-*
sudo zypper in --allow-unsigned-rpm --no-confirm dkms*
sudo zypper in --allow-unsigned-rpm --no-confirm nvidia*
sudo zypper in --allow-unsigned-rpm --no-confirm x11-video*
```  

If everything went well, we have the driver installed.
Now just run the command sudo ```nvidia-xconfig --no-logo``` and restart the machine
