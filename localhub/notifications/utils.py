# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from .emails import send_notification_email
from .models import Notification
from .webpush import send_notification_webpush


def bulk_create_and_send_notifications(notifications):
    """
    Shortcut: does bulk_create and then calls send() for each object.
    """
    notifications = list(notifications)
    if not notifications:
        return []
    for notification in Notification.objects.bulk_create(notifications):
        send_notification_email(notification)
        send_notification_webpush(notification)
    return notifications
