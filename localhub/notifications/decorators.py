# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools

from .registry import registry


def register(model):
    """Class decorator that registers a notification Adapter
    class with this model.

    Example:

    @register(Post)
    class PostAdapter(DefaultAdapter):
        ...

    Args:
        model (Model): Django Model class

    Returns:
        Adapter: Adapter class
    """

    def _adapter_wrapper(adapter_cls):
        registry.register(adapter_cls, model)
        return adapter_cls

    return _adapter_wrapper


def dispatch(func):
    """Handles email and push messages for all notifications returned. Notifications
    are automatically saved to the database.

    Check is run on all notifications to ensure only permitted verbs are saved
    and dispatched.

    Args:
        func (function): Method or function returning a single instance
        or iterable of Notification instances.

    Returns:
        list: saved Notification instances.
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
