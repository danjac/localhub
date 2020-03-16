# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools

from .registry import registry


def register(model):
    def _adapter_wrapper(adapter_cls):
        registry.register(adapter_cls, model)
        return adapter_cls

    return _adapter_wrapper


def dispatch(func):
    """
    Method should return a list of Notification instances. Runs
    bulk_create() on the notifications and calls dispatch() on
    each notification.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from .models import Notification

        notifications = list(func(*args, **kwargs))
        if not notifications:
            return []
        for notification in Notification.objects.bulk_create(notifications):
            registry.get_adapter(notification).send_notification()
        return notifications

    return wrapper
