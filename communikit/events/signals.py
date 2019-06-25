# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from communikit.events import tasks
from communikit.events.models import Event
from communikit.notifications.emails import send_notification_email


@receiver(post_delete, sender=Event, dispatch_uid="events.delete_flags")
def delete_flags(instance: Event, **kwargs):
    transaction.on_commit(lambda: instance.get_flags().delete())


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
    transaction.on_commit(instance.make_search_updater())


@receiver(post_save, sender=Event, dispatch_uid="events.send_notifications")
def send_notifications(instance: Event, created: bool, **kwargs):
    def notify():
        subjects = {
            "mentioned": _("You have been mentioned in an event"),
            "created": _("A new event has been added"),
            "updated": _("An event has been updated"),
        }
        event_url = instance.get_permalink()
        for notification in instance.notify(created):
            send_notification_email(
                notification,
                subjects[notification.verb],
                event_url,
                "events/emails/notification.txt",
            )

    transaction.on_commit(notify)
