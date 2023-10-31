flavor=%1
cp -a /usr/src/kernel-modules/nvidia-%{-v*}-$flavor/Makefile{,.tmp} || true
make -C /usr/src/kernel-modules/nvidia-%{-v*}-$flavor clean || true
mv /usr/src/kernel-modules/nvidia-%{-v*}-$flavor/Makefile{.tmp,} || true
if [ "$1" = 0 ] ; then
    # cleanup of bnc# 1000625
    rm -f /usr/lib/tmpfiles.d/nvidia-logind-acl-trick-G02.conf
fi

