#  Copyright 2005 Adam Jackson.
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  on the rights to use, copy, modify, merge, publish, distribute, sub
#  license, and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice (including the next
#  paragraph) shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.  IN NO EVENT SHALL
#  ADAM JACKSON BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Process this file with autoconf to produce a configure script

# Initialize Autoconf
AC_PREREQ([2.60])
AC_INIT([xf86-input-libinput],
        [1.1.0],
        [https://gitlab.freedesktop.org/xorg/driver/xf86-input-libinput/issues],
        [xf86-input-libinput])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR(.)

# Initialize Automake
AM_INIT_AUTOMAKE([foreign dist-bzip2])

# Initialize libtool
AC_DISABLE_STATIC
LT_INIT

# Initialize X.Org macros 1.8 or later for MAN_SUBSTS set by XORG_MANPAGE_SECTIONS
m4_ifndef([XORG_MACROS_VERSION],
          [m4_fatal([must install xorg-macros 1.8 or later before running autoconf/autogen])])
XORG_MACROS_VERSION(1.8)
XORG_DEFAULT_OPTIONS

# Obtain compiler/linker options from server and required extensions
PKG_CHECK_MODULES(XORG, [xorg-server >= 1.19] xproto [inputproto >= 2.2])
PKG_CHECK_MODULES(LIBINPUT, [libinput >= 1.11.0])

OLD_LIBS=$LIBS
OLD_CFLAGS=$CFLAGS
LIBS="$LIBS $LIBINPUT_LIBS"
CFLAGS="$CFLAGS $LIBINPUT_CFLAGS"

AC_MSG_CHECKING([if libinput_device_config_scroll_get_button_lock is available])
AC_LINK_IFELSE(
               [AC_LANG_PROGRAM([[#include <libinput.h>]],
                                [[libinput_device_config_scroll_get_button_lock(NULL)]])],
               [AC_MSG_RESULT([yes])
                AC_DEFINE(HAVE_LIBINPUT_SCROLL_BUTTON_LOCK, [1],
                          [libinput_device_config_scroll_get_button_lock() is available])
                [libinput_have_scroll_button_lock=yes]],
               [AC_MSG_RESULT([no])
                [libinput_have_scroll_button_lock=no]])
LIBS=$OLD_LIBS
CFLAGS=$OLD_CFLAGS

# Define a configure option for an alternate input module directory
AC_ARG_WITH(xorg-module-dir,
            AC_HELP_STRING([--with-xorg-module-dir=DIR],
                           [Default xorg module directory [[default=$libdir/xorg/modules]]]),
            [moduledir="$withval"],
            [moduledir="$libdir/xorg/modules"])
inputdir=${moduledir}/input
AC_SUBST(inputdir)

AC_ARG_WITH(xorg-conf-dir,
            AC_HELP_STRING([--with-xorg-conf-dir=DIR],
                           [Default xorg.conf.d directory [[default=${prefix}/share/X11/xorg.conf.d]]]),
            [xorgconfdir="$withval"],
            [xorgconfdir='${prefix}/share/X11/xorg.conf.d'])
AC_SUBST(xorgconfdir)

# X Server SDK location is required to install header files
sdkdir=`$PKG_CONFIG --variable=sdkdir xorg-server`

# Workaround overriding sdkdir to be able to create a tarball when user has no
# write permission in sdkdir. See DISTCHECK_CONFIGURE_FLAGS in Makefile.am
AC_ARG_WITH([sdkdir], [], [sdkdir="$withval"])
AC_SUBST([sdkdir])

DRIVER_NAME=libinput
AC_SUBST([DRIVER_NAME])

AC_CONFIG_FILES([Makefile
		 include/Makefile
		 src/Makefile
		 man/Makefile
		 test/Makefile
		 xorg-libinput.pc])
AC_OUTPUT
