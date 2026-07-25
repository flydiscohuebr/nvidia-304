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

#include <assert.h>
#include <math.h>
#include <stdio.h>

#include "bezier.h"

const struct bezier_control_point bezier_defaults[4] = {
	{ 0.0, 0.0 },
	{ 0.0, 0.0 },
	{ 1.0, 1.0 },
	{ 1.0, 1.0 },
};

struct point {
	int x, y;
};

/**
 * de Casteljau's algorithm. See this page here
 * https://pomax.github.io/bezierinfo/#extended
 *
 * To play with bezier curve shapes, I used
 * http://cubic-bezier.com/
 */
static struct point
decasteljau(const struct point *controls,
	    size_t ncontrols,
	    double t)
{
	struct point new_controls[ncontrols];

	if (ncontrols == 1)
		return controls[0];

	for (int i = 0; i < ncontrols - 1; i++) {
		new_controls[i].x = (1.0 - t) * controls[i].x + t * controls[i + 1].x;
		new_controls[i].y = (1.0 - t) * controls[i].y + t * controls[i + 1].y;
	}

	return decasteljau(new_controls, ncontrols - 1, t);
}

/**
 * Given a Bézier curve defined by the control points, reduce the curve to
 * one with ncurve_points.
 */
static void
flatten_curve(const struct point *controls,
	      size_t ncontrols,
	      struct point *curve,
	      size_t ncurve_points)
{
	ncurve_points--; /* make sure we end up with 100/100 as last point */

	for (int i = 0; i <= ncurve_points; i++) {
		double t = 1.0 * i/ncurve_points;
		struct point p;

		p = decasteljau(controls, ncontrols, t);
		curve[i] = p;
	}
}

/**
 * Calculate line through a and b, set curve[x] for each x between
 * [a.x,  b.x].
 *
 * Note: pcurve must be at least b.x size.
 */
static void
line_between(struct point a, struct point b,
	     struct point *curve, size_t curve_sz)
{
	double slope;
	double offset;

	assert(b.x < curve_sz);

	if (a.x == b.x) {
		curve[a.x].x = a.x;
		curve[a.x].y = a.y;
		return;
	}

	slope = (double)(b.y - a.y)/(b.x - a.x);
	offset = a.y - slope * a.x;

	for (int x = a.x; x <= b.x; x++) {
		struct point p;
		p.x = x;
		p.y = slope * x + offset;
		curve[x] = p;
	}
}

bool
cubic_bezier(const struct bezier_control_point controls[4],
	     int *bezier_out,
	     size_t bezier_sz)
{
	const int nsegments = 50;
	const int range = bezier_sz - 1;
	struct point curve[nsegments];
	struct point bezier[bezier_sz];
	struct point zero = { 0, 0 },
		     max = { range, range};

	/* Scale control points into the [0, bezier_sz) range */
	struct point ctrls[4];

	for (int i = 0; i < 4; i++) {
		if (controls[i].x < 0.0 || controls[i].x > 1.0 ||
		    controls[i].y < 0.0 || controls[i].y > 1.0)
			return false;

		ctrls[i].x = controls[i].x * range;
		ctrls[i].y = controls[i].y * range;
	}

	for (int i = 0; i < 3; i++) {
		if (ctrls[i].x > ctrls[i+1].x)
			return false;
	}

	/* Reduce curve to nsegments, because this isn't a drawing program */
	flatten_curve(ctrls, 4, curve, nsegments);

	/* we now have nsegments points in curve that represent the bezier
	   curve (already in the [0, bezier_sz) range). Run through the
	   points and draw a straight line between each point and voila, we
	   have our curve.

	   If the first control points (x0/y0) is not at x == 0 or the last
	   control point (x3/y3) is not at the max value, draw a line
	   between from 0/0 to x0/y0 and from x3/y3 to xmax/y3.
	 */

	line_between(zero, curve[0], bezier, bezier_sz);

	for (int i = 0; i < nsegments - 1; i++)
		line_between(curve[i], curve[i+1], bezier, bezier_sz);

	if (curve[nsegments - 1].x < max.x)
		line_between(curve[nsegments - 1], max, bezier, bezier_sz);

	for (int i = 0; i < bezier_sz; i++)
		bezier_out[i] = bezier[i].y;

	return true;
}
