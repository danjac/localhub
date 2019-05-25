# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

# from communikit.photos.emails import send_notification_email
from communikit.photos.models import Photo


@receiver(
    post_save, sender=Photo, dispatch_uid="photos.update_search_document"
)
def update_search_document(instance: Photo, **kwargs):
    transaction.on_commit(instance.make_search_updater())


"""
@receiver(post_save, sender=Photo, dispatch_uid="photos.send_notifications")
def send_notifications(instance: Photo, created: bool, **kwargs):
    def notify():
        for notification in instance.notify(created):
            send_notification_email(notification)

    transaction.on_commit(notify)
"""
