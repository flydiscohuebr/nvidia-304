#!/bin/sh

driver_version=$(grep -i ^version: nvidia-gfxG0?.spec |awk -F" " '{print $2}')

for arch in x86 x86_64; do
  file=NVIDIA-Linux-${arch}-${driver_version}.run
  if [ ! -s ${file} ]; then
    echo -n "Dowloading ${file} ... "
    curl -s -o $file ftp://download.nvidia.com/XFree86/Linux-${arch}/${driver_version}/$file
    echo "done"
  else
    echo -n "Checking   ${file}: "
    sh ${file} --check
    if [ $? -ne 0 ]; then
      rm ${file} 
      echo -n "Dowloading ${file} ... "
      curl -s -o $file ftp://download.nvidia.com/XFree86/Linux-${arch}/${driver_version}/$file 
      echo "done"
    fi
  fi
done
