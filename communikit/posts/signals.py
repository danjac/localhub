# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from communikit.notifications.emails import send_notification_email
from communikit.posts import tasks
from communikit.posts.models import Post


@receiver(post_save, sender=Post, dispatch_uid="posts.fetch_title_from_link")
def fetch_title_from_url(instance: Post, **kwargs):
    tasks.fetch_title_from_url(instance.id)


@receiver(post_save, sender=Post, dispatch_uid="posts.update_search_document")
def update_search_document(instance: Post, **kwargs):
    transaction.on_commit(instance.make_search_updater())


@receiver(post_save, sender=Post, dispatch_uid="posts.send_notifications")
def send_notifications(instance: Post, created: bool, **kwargs):
    def notify():
        subjects = {
            "mentioned": _("You have been mentioned in a post"),
            "created": _("A new post has been added"),
            "updated": _("A post has been updated"),
        }
        post_url = instance.get_permalink()
        for notification in instance.notify(created):
            send_notification_email(
                notification,
                subjects[notification.verb],
                post_url,
                "posts/emails/notification.txt",
            )

    transaction.on_commit(notify)
