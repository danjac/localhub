from django.dispatch import receiver
from django.db.models.signals import pre_save

from communikit.events import tasks
from communikit.events.models import Event


@receiver(pre_save, sender=Event, dispatch_uid="events.update_coordinates")
def update_event_coordinates(instance: Event, created: bool = False, **kwargs):
    if created or instance.tracker.has_changed("location"):
        tasks.update_event_coordinates.delay(instance.id)
