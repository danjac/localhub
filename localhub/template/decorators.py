# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools


def with_cached_context_value(tag):
    """
    Use with simple_tag. Caches a value in the template
    context. Useful for DB-intensive operations where
    we just want to calculate once in a request.

    Example:

    @register.simple_tag(takes_context=True)
    @with_cached_context_value
    def notification_count(context, user):
        return user.get_notification_count()
    """

    @functools.wraps(tag)
    def wrapper(context, *args, **kwargs):
        if (cache_key := f"_{tag.__name__}_cached") in context:
            return context[cache_key]
        context[cache_key] = tag(context, *args, **kwargs)
        return context[cache_key]

    return wrapper
