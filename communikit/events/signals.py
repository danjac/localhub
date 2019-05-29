from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from communikit.events import tasks
from communikit.events.emails import send_notification_email
from communikit.events.models import Event


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
        for notification in instance.notify(created):
            send_notification_email(notification)

    transaction.on_commit(notify)
