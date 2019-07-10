# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from localite.comments.models import Comment
from localite.notifications.emails import send_notification_email


@receiver(
    post_save, sender=Comment, dispatch_uid="comments.send_notifications"
)
def send_notifications(instance: Comment, created: bool, **kwargs):
    def notify():
        subjects = {
            "mentioned": _("You have been mentioned in a comment"),
            "created": _("A new comment has been added"),
            "updated": _("A comment has been updated"),
            "commented": _("Someone has commmented on one of your posts"),
        }
        comment_url = instance.get_permalink()
        for notification in instance.notify(created):
            send_notification_email(
                notification,
                subjects[notification.verb],
                comment_url,
                "comments/emails/notification.txt",
            )

    transaction.on_commit(notify)
