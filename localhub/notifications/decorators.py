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

        notifications = func(*args, **kwargs)

        if not notifications:
            return []

        if isinstance(notifications, Notification):
            notifications = [notifications]
        else:
            notifications = list(notifications)

        for_create = []
        adapters = []

        for notification in notifications:
            adapter = registry.get_adapter(notification)
            if adapter.is_allowed():
                for_create.append(notification)
                adapters.append(adapter)

        Notification.objects.bulk_create(for_create)

        for adapter in adapters:
            adapter.send_notification()
        return notifications

    return wrapper
