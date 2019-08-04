# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from localhub.events import tasks
from localhub.events.models import Event


@receiver(
    post_save, sender=Event, dispatch_uid="events.update_event_coordinates"
)
def update_event_coordinates(instance: Event, created: bool = False, **kwargs):
    if created or instance.location_tracker.changed():
        transaction.on_commit(
            lambda: tasks.update_event_coordinates.delay(instance.id)
        )


@receiver(
    post_save, sender=Event, dispatch_uid="events.update_search_document"
)
def update_search_document(instance: Event, **kwargs):
    transaction.on_commit(lambda: instance.search_indexer.update())


@receiver(post_save, sender=Event, dispatch_uid="events.taggit")
def taggit(instance: Event, created: bool, **kwargs):
    transaction.on_commit(lambda: instance.taggit(created))
