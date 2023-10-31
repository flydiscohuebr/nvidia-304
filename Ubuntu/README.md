Run the command ```dpkg-buildpackage -b -us -uc```

If dependencies are missing, you can install them manually or use the command below
```apt-get install     --yes $(dpkg-checkbuilddeps 2>&1 | sed -e 's/dpkg-checkbuilddeps:\serror:\sUnmet build dependencies: //g' -e  's/[\(][^)]*[\)] //g')```

You can download xorg 1.19 here
http://archive.ubuntu.com/ubuntu/pool/main/x/xorg-server/xserver-xorg-core_1.19.6-1ubuntu4.15_amd64.deb
SHA512:341febec443450fd37e20cc82f7c4ad14dc66bf0370e3344773d19ff9036ad18063713c93f68390ce11a048c4e3d6a65690a5ad756f6aebb376b7d3b27e49610
