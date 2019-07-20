# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from simple_history.signals import post_create_historical_record

from localhub.activities.signals import send_notifications
from localhub.photos.models import Photo


@receiver(
    post_save, sender=Photo, dispatch_uid="photos.update_search_document"
)
def update_search_document(instance: Photo, **kwargs):
    transaction.on_commit(instance.make_search_updater())


@receiver(post_save, sender=Photo, dispatch_uid="photos.taggit")
def taggit(instance: Photo, created: bool, **kwargs):
    transaction.on_commit(lambda: instance.taggit(created))


receiver(
    post_create_historical_record,
    sender=Photo.history.model,
    dispatch_uid="photos.send_notifications",
)(send_notifications)
