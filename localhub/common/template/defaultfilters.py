# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template


register = template.Library()


@register.filter
def from_dictkey(dct, key, default=None):
    """
    Returns value from a dict.
    """
    if not dct:
        return default
    return dct.get(key, default)
