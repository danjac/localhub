# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools

from .models import Notification


def dispatch(func):
    """
    Method should return a list of Notification instances. Runs
    bulk_create() on the notifications and calls dispatch() on
    each notification.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        notifications = list(func(*args, **kwargs))
        if not notifications:
            return []
        for notification in Notification.objects.bulk_create(notifications):
            notification.get_adapter().send_notification()
        return notifications

    return wrapper
