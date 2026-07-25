/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright © 2013-2015 Red Hat, Inc.
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

#include "draglock.h"

#include <assert.h>
#include <string.h>

static void
test_config_empty(void)
{
	struct draglock dl;
	int rc;

	rc = draglock_init_from_string(&dl, NULL);
	assert(dl.mode == DRAGLOCK_DISABLED);
	assert(rc == 0);
}

static void
test_config_invalid(void)
{
	struct draglock dl;
	int rc;

	/* no trailing space */
	rc = draglock_init_from_string(&dl, "1 ");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "256");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "-1");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "1 2 3");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "0 2");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "0 0");
	assert(rc != 0);
	assert(dl.mode == DRAGLOCK_DISABLED);
}

static void
test_config_disable(void)
{
	struct draglock dl;
	int rc;

	rc = draglock_init_from_string(&dl, "");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_init_from_string(&dl, "0");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);
}

static void
test_config_meta_button(void)
{
	struct draglock dl;
	int rc;

	rc = draglock_init_from_string(&dl, "1");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_META);
	assert(dl.meta_button == 1);

	rc = draglock_init_from_string(&dl, "2");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_META);
	assert(dl.meta_button == 2);

	rc = draglock_init_from_string(&dl, "10");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_META);
	assert(dl.meta_button == 10);
}

static void
test_config_button_pairs(void)
{
	struct draglock dl;
	int rc;

	rc = draglock_init_from_string(&dl, "1 1");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_PAIRS);

	rc = draglock_init_from_string(&dl, "1 2 3 4 5 6 7 8");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_PAIRS);

	rc = draglock_init_from_string(&dl, "1 2 3 4 5 0 7 8");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_PAIRS);

	/* all disabled */
	rc = draglock_init_from_string(&dl, "1 0 3 0 5 0 7 0");
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);
}

static void
test_config_get(void)
{
	struct draglock dl;
	int rc;
	const int sz = 32;
	int map[sz];

	draglock_init_from_string(&dl, "");
	rc = draglock_get_meta(&dl);
	assert(rc == 0);
	rc = draglock_get_pairs(&dl, map, sz);
	assert(rc == 0);

	draglock_init_from_string(&dl, "8");
	rc = draglock_get_meta(&dl);
	assert(rc == 8);
	rc = draglock_get_pairs(&dl, map, sz);
	assert(rc == 0);

	draglock_init_from_string(&dl, "1 2 3 4 5 6");
	rc = draglock_get_meta(&dl);
	assert(rc == 0);
	rc = draglock_get_pairs(&dl, map, sz);
	assert(rc == 5);
	assert(map[0] == 0);
	assert(map[1] == 2);
	assert(map[2] == 0);
	assert(map[3] == 4);
	assert(map[4] == 0);
	assert(map[5] == 6);
}

static void
test_set_meta(void)
{
	struct draglock dl;
	int rc;

	draglock_init_from_string(&dl, "");

	rc = draglock_set_meta(&dl, 0);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_set_meta(&dl, 1);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_META);

	rc = draglock_set_meta(&dl, -1);
	assert(rc == 1);
	rc = draglock_set_meta(&dl, 32);
	assert(rc == 1);
}

static void
test_set_pairs(void)
{
	struct draglock dl;
	int rc;
	const int sz = 32;
	int map[sz];

	draglock_init_from_string(&dl, "");
	memset(map, 0, sizeof(map));

	rc = draglock_set_pairs(&dl, map, sz);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	rc = draglock_set_pairs(&dl, map, 1);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_DISABLED);

	map[0] = 1;
	rc = draglock_set_pairs(&dl, map, 1);
	assert(rc == 1);

	map[0] = 0;
	map[1] = 2;
	rc = draglock_set_pairs(&dl, map, sz);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_PAIRS);

	map[0] = 0;
	map[1] = 0;
	map[10] = 8;
	rc = draglock_set_pairs(&dl, map, sz);
	assert(rc == 0);
	assert(dl.mode == DRAGLOCK_PAIRS);
}

static void
test_filter_meta_passthrough(void)
{
	struct draglock dl;
	int rc;
	int button, press;
	int i;

	rc = draglock_init_from_string(&dl, "10");

	for (i = 0; i < 10; i++) {
		button = i;
		press = 1;

		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);
		assert(press == 1);

		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);
		assert(press == 1);
	}
}

static void
test_filter_meta_click_meta_only(void)
{
	struct draglock dl;
	int rc;
	int button, press;

	rc = draglock_init_from_string(&dl, "10");

	button = 10;
	press = 1;

	rc = draglock_filter_button(&dl, &button, &press);
	assert(rc == 0);
	assert(button == 0);

	button = 10;
	press = 0;
	rc = draglock_filter_button(&dl, &button, &press);
	assert(rc == 0);
	assert(button == 0);
}

static void
test_filter_meta(void)
{
	struct draglock dl;
	int rc;
	int button, press;
	int i;

	rc = draglock_init_from_string(&dl, "10");

	for (i = 1; i < 10; i++) {
		/* meta down */
		button = 10;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* meta up */
		button = 10;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button down -> passthrough */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);

		/* button up -> eaten */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button down -> eaten */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button up -> passthrough */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);
		assert(press == 0);
	}
}

static void
test_filter_meta_extra_click(void)
{
	struct draglock dl;
	int rc;
	int button, press;
	int i;

	rc = draglock_init_from_string(&dl, "10");

	for (i = 1; i < 10; i++) {
		/* meta down */
		button = 10;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* meta up */
		button = 10;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button down -> passthrough */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);

		/* button up -> eaten */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* meta down */
		button = 10;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* meta up */
		button = 10;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button down -> eaten */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button up -> passthrough */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);
		assert(press == 0);
	}
}

static void
test_filter_meta_interleaved(void)
{
	struct draglock dl;
	int rc;
	int button, press;
	int i;

	rc = draglock_init_from_string(&dl, "10");

	for (i = 1; i < 10; i++) {
		/* meta down */
		button = 10;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* meta up */
		button = 10;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button down -> passthrough */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);

		/* button up -> eaten */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);
	}

	for (i = 0; i < 10; i++) {
		/* button down -> eaten */
		button = i;
		press = 1;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == 0);

		/* button up -> passthrough */
		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		assert(button == i);
		assert(press == 0);
	}
}

static void
test_filter_pairs(void)
{
	struct draglock dl;
	int rc;
	int button, press;
	int i;

	rc = draglock_init_from_string(&dl, "1 11 2 0 3 13 4 0 5 15 6 0 7 17 8 0 9 19");

	for (i = 1; i < 10; i++) {
		button = i;
		press = 1;

		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		if (i % 2)
			assert(button == i + 10);
		else
			assert(button == i);
		assert(press == 1);

		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		if (i % 2) {
			assert(button == 0);
		} else {
			assert(button == i);
			assert(press == 0);
		}
	}

	for (i = 1; i < 10; i++) {
		button = i;
		press = 1;

		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		if (i % 2) {
			assert(button == 0);
		} else {
			assert(button == i);
			assert(press == 1);
		}

		button = i;
		press = 0;
		rc = draglock_filter_button(&dl, &button, &press);
		assert(rc == 0);
		if (i % 2)
			assert(button == i + 10);
		else
			assert(button == i);
		assert(press == 0);
	}
}

int
main(int argc, char **argv)
{
	test_config_empty();
	test_config_invalid();
	test_config_disable();
	test_config_meta_button();
	test_config_button_pairs();

	test_config_get();
	test_set_meta();
	test_set_pairs();

	test_filter_meta_passthrough();
	test_filter_meta_click_meta_only();
	test_filter_meta();
	test_filter_meta_extra_click();
	test_filter_meta_interleaved();

	test_filter_pairs();

	return 0;
}
