# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _


from localhub.flags.models import Flag
from localhub.notifications.emails import send_notification_email


EMAIL_TEMPLATES = {
    "comment": "comments/emails/notification.txt",
    "event": "events/emails/notification.txt",
    "photo": "photos/emails/notification.txt",
    "post": "posts/emails/notification.txt",
}

EMAIL_SUBJECTS = {
    "comment": _("A comment has been flagged"),
    "event": _("An event has been flagged"),
    "photo": _("A photo has been flagged"),
    "post": _("A post has been flagged"),
}


@receiver(post_save, sender=Flag, dispatch_uid="flags.send_notifications")
def send_notifications(instance: Flag, created: bool, **kwargs):
    def notify():
        for notification in instance.notify():
            send_notification_email(
                notification,
                EMAIL_SUBJECTS[notification.content_type.name],
                notification.content_object.get_permalink(),
                EMAIL_TEMPLATES[notification.content_type.name],
            )

    if created:
        transaction.on_commit(notify)
