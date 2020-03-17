# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.dispatch import receiver

from localhub.notifications.signals import notification_read

from .models import Message


@receiver(
    notification_read,
    sender=Message,
    dispatch_uid="localhub.private_messages.message_notification_read",
)
def message_notification_read(instance, **kwargs):
    instance.mark_read()