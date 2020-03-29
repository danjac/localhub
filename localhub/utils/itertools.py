# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import itertools


def takefirst(iterable, key=None):
    """Returns iterable containing just the first instance of
    an item in the list matching the key

    Args:
        iterable
        key (any, optional): key value or function (default: None)

    Yields:
        any
    """

    keys = set()

    for key, group in itertools.groupby(iterable, key):
        for item in group:
            if key not in keys:
                keys.add(key)
                yield item
