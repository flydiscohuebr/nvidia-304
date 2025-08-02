**Before starting, install these dependencies with the command below**  
```
sudo apt install libx11-6:i386 libxext6:i386 libc6:i386
```  

**Note for Ubuntu 25.04 users:**  
In case of errors during build, run the dpkg-buildpackage command with fakeroot  
> I haven't yet tried to find out why, but for now I'll keep it that way
```
fakeroot dpkg-buildpackage -b -uc -us
```  

Since you are doing this I assume you know how to navigate between directories through the terminal or at least have the notion of right-clicking in your file explorer and clicking on the "Open terminal here" option.  

In the directory where the three folders are located, we will enter them one by one to build the necessary packages.  

We will start with the xorg 1.19, to do this, enter the xorg-server folder and run some commands below.  

Install the necessary dependencies to build the package. The command below will serve for this purpose.
```
sudo apt build-dep .
```  

Now to build the package just run the following command:  
```
dpkg-buildpackage -b -us -uc
```  

If there are no errors during the build, you will be provided with several .deb files in the previous directory. For now, leave the files there and let's move on to the next package  

Now we enter the **nvidia-settings** folder  
Install the necessary dependencies to build the package.  
```
sudo apt build-dep .
```  

Build the package with the command below:  
```
dpkg-buildpackage -b -us -uc
```  

Now let's go to the last folder **nvidia-graphics-drivers**  
Install the necessary dependencies to build the package.  
```
sudo apt build-dep .
```  

Before building the package we will need the .run files provided by nvidia to do this run the command below this will download them into their specific folders  
```
dpkg-buildpackage -Tget-orig-source
```

Now we build the packages  
```
dpkg-buildpackage -b -us -uc
```  

You will also need the xserver-xorg-input-libinput package in version 1.1.0 or lower  
To make things easier, I recommend that you use the package below, which was downloaded from the Ubuntu repository (old versions)  
https://old-releases.ubuntu.com/ubuntu/pool/main/x/xserver-xorg-input-libinput/xserver-xorg-input-libinput_1.1.0-1_amd64.deb
<details>
    <summary>xserver-xorg-input-libinput SHA512</summary>
SHA512: 512a81db07cfd340fdd3cf75be20c08ff6c948b5c531851bca35c10fbc1b505c0b3a5d9eab3e8d0107667089763a82e378576b64fc880387f3f242227e15a4da
</details>  


Downgrade and hold xorg updates  
Just remember that the commands below are being run in the folder containing the built files (this includes the xserver-xorg-input-libinput downloaded above)  
If the file is in another location, you need to indicate the directory  
```
sudo apt install ./xserver-xorg-input-libinput_1.1.0-1_amd64.deb
sudo apt install ./xserver-xorg-core_1.19.6-1ubuntu* --allow-downgrades
sudo apt-mark hold xserver-xorg-core xserver-xorg-input-libinput
```  

Install the generated packages from nvidia-graphics-drivers and nvidia-settings  
```
sudo apt install ./nvidia-304_*.deb
sudo apt install ./nvidia-settings*.deb
```  

Run the command ```nvidia-xconfig --no-logo``` to create xorg.conf then run the commands above 
```
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/nvidia-304/xorg\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i /'Section "Files"'/,/'EndSection'/s%'EndSection'%"\tModulePath \"/usr/lib/xorg/modules\" \nEndSection"%g /etc/X11/xorg.conf
sudo sed -i 's/HorizSync/#HorizSync/' /etc/X11/xorg.conf
sudo sed -i 's/VertRefresh/#VertRefresh/' /etc/X11/xorg.conf
```  
Now restart the computer  

If something doesn't work, take a look at the link below for possible solutions.  
https://github.com/flydiscohuebr/nvidia-304#issues
