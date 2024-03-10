REQPKGS=(libinput xorg-server bigreqsproto compositeproto damageproto dbus-1 dmx dri dri2proto dri3proto egl epoxy fixesproto fontconfig fontenc fontsproto fontutil freetype2 gbm gl glproto ice inputproto kbproto libdrm libsystemd libudev openssl pciaccess pixman-1 presentproto randrproto renderproto resourceproto scrnsaverproto sm wayland-client wayland-protocols x11 xau xaw7 xcb-aux xcb-icccm xcb-image xcb-keysyms xcb-renderutil xcmiscproto xdmcp xext xextproto xf86dgaproto xf86driproto xfixes xfont2 xi xineramaproto xkbfile xmu xorg-macros xp xpm xprintutil xproto xrender xres xshmfence xt xtrans xtst xv)

sudo zypper up

for pkg in "${REQPKGS[@]}"; do
    if yum -q list installed "$pkg" > /dev/null 2>&1; then
        echo -e "$pkg is already installed"
    else
        sudo zypper --no-refresh in -yC "pkgconfig($pkg)"
    fi
done

sudo zypper in -y flex libtool kernel-syms kernel-source update-desktop-files

#for pkg in "${REQPKGS[@]}"; do
#    if yum -q list installed "$pkg" > /dev/null 2>&1; then
#        echo -e "$pkg is already installed"
#    else
#        yum install "$pkg" -y && echo "Successfully installed $pkg"
#    fi
#done