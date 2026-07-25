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

#include "bezier.h"

#include <assert.h>
#include <string.h>
#include <stdio.h>

static inline void
print_curve(int *bezier, size_t size)
{
	/* look at it with gnuplot, "plot 'output-file.txt'" */
	for (int i = 0; i < size; i++)
		printf("%d %d\n", i, bezier[i]);
}

static void
test_linear(void)
{
	const int size = 2048;
	int bezier[size];

	struct bezier_control_point controls[] = {
		{ 0.0, 0.0 },
		{ 0.0, 0.0 },
		{ 1.0, 1.0 },
		{ 1.0, 1.0 }
	};

	cubic_bezier(controls, bezier, size);

	assert(bezier[0] == 0);
	assert(bezier[size - 1] == size - 1);

	for (int x = 1; x < size; x++)
		assert(bezier[x] == x);
}

/* Center point pulled down towards X axis */
static void
test_flattened(void)
{
	const int size = 2048;
	int bezier[size];

	struct bezier_control_point controls[] = {
		{ 0.0, 0.0 },
		{ 0.1, 0.0 },
		{ 1.0, 0.9 },
		{ 1.0, 1.0 }
	};

	cubic_bezier(controls, bezier, size);

	assert(bezier[0] == 0);
	assert(bezier[size - 1] == size - 1);

	for (int x = 1; x < size - 1; x++) {
		assert(bezier[x] < x);
	}
}

/* Center point pulled up from X axis */
static void
test_raised(void)
{
	const int size = 2048;
	int bezier[size];

	struct bezier_control_point controls[] = {
		{ 0.0, 0.0 },
		{ 0.1, 0.4 },
		{ 0.4, 1.0 },
		{ 1.0, 1.0 }
	};

	cubic_bezier(controls, bezier, size);

	assert(bezier[0] == 0);
	assert(bezier[size - 1] == size - 1);

	for (int x = 1; x < size; x++)
		assert(bezier[x] >= x);

	for (int x = 10; x < size - 10; x++)
		assert(bezier[x] > x);
}

static void
test_windy(void)
{
	const int size = 2048;
	int bezier[size];

	struct bezier_control_point controls[] = {
		{ 0.0, 0.0 },
		{ 0.0, 0.3 },
		{ 1.0, 0.7 },
		{ 1.0, 1.0 }
	};

	cubic_bezier(controls, bezier, size);

	assert(bezier[0] == 0);
	assert(bezier[size - 1] == size - 1);

	for (int x = 1; x < size/2 - 20; x++)
		assert(bezier[x] > x);

	for (int x = size/2 + 20; x < size - 1; x++)
		assert(bezier[x] < x);
}

static void
test_nonzero_x_linear(void)
{
	const int size = 2048;
	int bezier[size];
	int x;

	struct bezier_control_point controls[] = {
		{ 0.2, 0.0 },
		{ 0.2, 0.0 },
		{ 0.8, 1.0 },
		{ 0.8, 1.0 }
	};

	cubic_bezier(controls, bezier, size);

	x = 0;
	do {
		assert(bezier[x] == 0);
	} while (++x < size * 0.2 - 1);

	/* ppc64le, ppc64, aarch64 have different math results at -O2,
	   resulting in one extra zero at the beginning of the array.
	   some other numbers are different too but within the error
	   margin (#99992) */
	if (bezier[x] == 0)
		x++;

	do {
		assert(bezier[x] > bezier[x-1]);
	} while (++x < size * 0.8 - 1);

	do {
		assert(bezier[x] == size - 1);
	} while (++x < size);
}

static void
test_nonzero_y_linear(void)
{
	const int size = 2048;
	int bezier[size];

	struct bezier_control_point controls[] = {
		{ 0.0, 0.2 },
		{ 0.0, 0.2 },
		{ 1.0, 0.8 },
		{ 1.0, 0.8 }
	};

	cubic_bezier(controls, bezier, size);

	assert(bezier[0] == (int)(size * 0.2));

	for (int x = 1; x < size; x++) {
		assert(bezier[x - 1] <= bezier[x]);
		assert(bezier[x] >= (int)(size * 0.2));
	}
}

int
main(int argc, char **argv)
{
	test_linear();
	test_flattened();
	test_raised();
	test_windy();
	test_nonzero_x_linear();
	test_nonzero_y_linear();

	return 0;
}
