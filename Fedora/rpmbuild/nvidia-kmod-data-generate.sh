wget https://download.nvidia.com/XFree86/Linux-x86_64/304.137/NVIDIA-Linux-x86_64-304.137.run
wget https://download.nvidia.com/XFree86/Linux-x86/304.137/NVIDIA-Linux-x86-304.137.run
chmod +x NVIDIA-Linux-x86*
./NVIDIA-Linux-x86_64-304.137.run -x ; ./NVIDIA-Linux-x86-304.137.run -x
mv NVIDIA-Linux-x86-304.137 nvidiapkg-x86
mv NVIDIA-Linux-x86_64-304.137 nvidiapkg-x64
tar -cvJf nvidia-kmod-data-304.137.tar.xz nvidiapkg-x86 nvidiapkg-x64
mv nvidia-kmod-data-304.137.tar.xz SOURCES
rm -rf nvidiapkg-* NVIDIA-Linux-x86*