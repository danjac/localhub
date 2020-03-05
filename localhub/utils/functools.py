# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from contextlib import contextmanager


@contextmanager
def temp_attribute(obj, attrname, temp_value):
    """
    Temporarily assigns an attribute with given value 
    to object. Removes attribute afterwards if not
    originally belonging to obj, otherwise resets
    to old value.
    """
    has_attr = hasattr(obj, attrname)
    old_value = None
    if has_attr:
        old_value = getattr(obj, attrname)
    setattr(obj, attrname, temp_value)
    yield
    if has_attr:
        setattr(obj, attrname, old_value)
    else:
        delattr(obj, attrname)
