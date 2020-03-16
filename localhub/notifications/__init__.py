# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.utils.module_loading import autodiscover_modules

from .adapters import BaseNotificationAdapter, NotificationAdapter
from .decorators import dispatch, register

__all__ = ["register", "dispatch", "BaseNotificationAdapter", "NotificationAdapter"]


def autodiscover():
    autodiscover_modules("notifications")
