#!/bin/sh

DIRNAME=xorg-server-$( date +%Y%m%d )

rm -rf $DIRNAME
git clone git://git.freedesktop.org/git/xorg/xserver $DIRNAME
cd $DIRNAME
if [ -z "$1" ]; then
    git log | head -1
else
    git checkout $1
fi
git log | head -1 | awk '{ print $2 }' > ../commitid
git repack -a -d
cd ..
tar cf - $DIRNAME | xz -c9 > $DIRNAME.tar.xz
rm -rf $DIRNAME
