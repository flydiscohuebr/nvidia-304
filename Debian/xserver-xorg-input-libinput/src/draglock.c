/*
 * SPDX-License-Identifier: MIT
 *
 * Copyright © 2015 Red Hat, Inc.
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

#include "draglock.h"

#include <string.h>
#include <stdlib.h>

#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))

static int
draglock_parse_config(struct draglock *dl, const char *config)
{
    int button = 0, target = 0;
    const char *str = NULL;
    char *end_str = NULL;
    int pairs[DRAGLOCK_MAX_BUTTONS] = {0};

    if (!config)
	    return 0;

    /* empty string disables drag lock */
    if (*config == '\0') {
	    dl->mode = DRAGLOCK_DISABLED;
	    return 0;
    }

    /* check for a single-number string first, config is "<int>" */
    button = strtol(config, &end_str, 10);
    if (*end_str == '\0') {
	    if (button < 0 || button >= DRAGLOCK_MAX_BUTTONS)
		    return 1;
	    /* we allow for button 0 so stacked xorg.conf.d snippets can
	     * disable the config again */
	    if (button == 0) {
		    dl->mode = DRAGLOCK_DISABLED;
		    return 0;
	    }

	    return draglock_set_meta(dl, button);
    }

    dl->mode = DRAGLOCK_DISABLED;

    /* check for a set of button pairs, config is
     * "<int> <int> <int> <int>..." */
    str = config;
    while (*str != '\0') {
	    button = strtol(str, &end_str, 10);
	    if (*end_str == '\0')
		    return 1;

	    str = end_str;
	    target = strtol(str, &end_str, 10);
	    if (end_str == str)
		    return 1;
	    if (button <= 0 || button >= DRAGLOCK_MAX_BUTTONS || target >= DRAGLOCK_MAX_BUTTONS)
		    return 1;

	    pairs[button] = target;
	    str = end_str;
    }

    return draglock_set_pairs(dl, pairs, ARRAY_SIZE(pairs));
}

int
draglock_init_from_string(struct draglock *dl, const char *config)
{
	dl->mode = DRAGLOCK_DISABLED;

	dl->meta_button = 0;
	dl->meta_state = false;
	memset(dl->lock_pair, 0, sizeof(dl->lock_pair));
	memset(dl->lock_state, 0, sizeof(dl->lock_state));

	return draglock_parse_config(dl, config);
}

enum draglock_mode
draglock_get_mode(const struct draglock *dl)
{
	return dl->mode;
}

int
draglock_get_meta(const struct draglock *dl)
{
	if (dl->mode == DRAGLOCK_META)
		return dl->meta_button;
	return 0;
}

size_t
draglock_get_pairs(const struct draglock *dl, int *array, size_t nelem)
{
	unsigned int i;
	size_t last = 0;

	if (dl->mode != DRAGLOCK_PAIRS)
		return 0;

	/* size 1 array with the meta button */
	if (dl->meta_button) {
		*array = dl->meta_button;
		return 1;
	}

	/* size N array with a[0] == 0, the rest ordered by button number */
	memset(array, 0, nelem * sizeof(array[0]));
	for (i = 0; i < nelem && i < ARRAY_SIZE(dl->lock_pair); i++) {
		array[i] = dl->lock_pair[i];
		if (array[i] != 0 && i > last)
			last = i;
	}
	return last;
}

int
draglock_set_meta(struct draglock *dl, int meta_button)
{
	if (meta_button < 0 || meta_button >= DRAGLOCK_MAX_BUTTONS)
		return 1;

	dl->meta_button = meta_button;
	dl->mode = meta_button ? DRAGLOCK_META : DRAGLOCK_DISABLED;

	return 0;
}

int
draglock_set_pairs(struct draglock *dl, const int *array, size_t nelem)
{
	unsigned int i;

	if (nelem == 0 || array[0] != 0)
		return 1;

	for (i = 0; i < nelem; i++) {
		if (array[i] < 0 || array[i] >= DRAGLOCK_MAX_BUTTONS)
			return 1;
	}

	dl->mode = DRAGLOCK_DISABLED;
	for (i = 0; i < nelem; i++) {
		dl->lock_pair[i] = array[i];
		if (dl->lock_pair[i])
			dl->mode = DRAGLOCK_PAIRS;
	}

	return 0;
}

static int
draglock_filter_meta(struct draglock *dl, int *button, int *press)
{
	int b = *button,
	    is_press = *press;

	if (b == dl->meta_button) {
		if (is_press)
			dl->meta_state = true;
		*button = 0;
		return 0;
	}

	switch (dl->lock_state[b]) {
	case DRAGLOCK_BUTTON_STATE_NONE:
		if (dl->meta_state && is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_DOWN_1;
			dl->meta_state = false;
		}
		break;
	case DRAGLOCK_BUTTON_STATE_DOWN_1:
		if (!is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_UP_1;
			b = 0;
		}
		break;
	case DRAGLOCK_BUTTON_STATE_UP_1:
		if (is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_DOWN_2;
			b = 0;
		}
		break;
	case DRAGLOCK_BUTTON_STATE_DOWN_2:
		if (!is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_NONE;
		}
		break;
	}

	*button = b;

	return 0;
}

static int
draglock_filter_pair(struct draglock *dl, int *button, int *press)
{
	int b = *button,
	    is_press = *press;

	if (dl->lock_pair[b] == 0)
		return 0;

	switch (dl->lock_state[b]) {
	case DRAGLOCK_BUTTON_STATE_NONE:
		if (is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_DOWN_1;
			b = dl->lock_pair[b];
		}
		break;
	case DRAGLOCK_BUTTON_STATE_DOWN_1:
		if (!is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_UP_1;
			b = 0;
		}
		break;
	case DRAGLOCK_BUTTON_STATE_UP_1:
		if (is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_DOWN_2;
			b = 0;
		}
		break;
	case DRAGLOCK_BUTTON_STATE_DOWN_2:
		if (!is_press) {
			dl->lock_state[b] = DRAGLOCK_BUTTON_STATE_NONE;
			b = dl->lock_pair[b];
		}
		break;
	}

	*button = b;

	return 0;
}

int
draglock_filter_button(struct draglock *dl, int *button, int *is_press)
{
	if (*button == 0)
		return 0;

	switch(dl->mode) {
	case DRAGLOCK_DISABLED:
		return 0;
	case DRAGLOCK_META:
		return draglock_filter_meta(dl, button, is_press);
	case DRAGLOCK_PAIRS:
		return draglock_filter_pair(dl, button, is_press);
	default:
		abort();
		break;
	}

	return 0;
}
