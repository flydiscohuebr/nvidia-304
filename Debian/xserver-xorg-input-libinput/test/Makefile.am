AM_CPPFLAGS = $(XORG_CFLAGS) \
	      $(CWARNFLAGS) \
	      -I$(top_srcdir)/include \
	      -I$(top_srcdir)/src

tests = test-draglock test-bezier

noinst_PROGRAMS = $(tests)

test_draglock_SOURCES = test-draglock.c
test_draglock_LDADD = ../src/libdraglock.la

test_bezier_SOURCES = test-bezier.c
test_bezier_LDADD = ../src/libbezier.la -lm

TESTS = $(tests)
