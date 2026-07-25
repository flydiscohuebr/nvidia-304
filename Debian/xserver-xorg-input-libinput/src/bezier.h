/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright © 2016 Red Hat, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifndef BEZIER_H
#define BEZIER_H

#include <stdlib.h>
#include <stdbool.h>

struct bezier_control_point {
	double x, y;
};

extern const struct bezier_control_point bezier_defaults[4];

/**
 * Given four control points in the range [(0.0/0.0), (1.0/1.0)]
 * construct a Bézier curve.
 *
 *    ^
 *1.0 |    c2 ______ c3
 *    |     _/
 *    |    /
 *    |c1 /
 *    |  /
 *    | /
 *    |/_________________>
 *    c0           1.0
 *
 * This function requires that c[i].x <= c[i+1].x
 *
 * The curve is mapped into a canvas size [0, bezier_sz)². For each x
 * coordiante in [0, bezier_sz), the matching y coordinate is thus
 * bezier[x].
 *
 * In other words, if you have a range [0,2048) input possible values,
 * the output is a list of 2048 points in a [0, 2048) range.
 *
 * @return true on success, false otherwise
 */
bool
cubic_bezier(const struct bezier_control_point controls[4],
	     int *bezier,
	     size_t bezier_sz);
#endif
