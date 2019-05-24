# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from communikit.comments.emails import send_notification_email
from communikit.comments.models import Comment


@receiver(
    post_save, sender=Comment, dispatch_uid="comments.send_notifications"
)
def send_notifications(instance: Comment, created: bool, **kwargs):
    def notify():
        for notification in instance.notify(created):
            send_notification_email(notification)

    transaction.on_commit(lambda: notify)
