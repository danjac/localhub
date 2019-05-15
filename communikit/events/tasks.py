import geocoder

from celery import shared_task
from celery.utils.log import get_task_logger

from communikit.events.models import Event

logger = get_task_logger(__name__)


@shared_task
def update_event_coordinates(event_id: int):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        logger.info("event not found:%s", event_id)
        return

    if not event.location:
        Event.objects.filter(pk=event.id).update(latitude=None, longitude=None)
        return

    result = geocoder.osm(event.location)
    if not result.ok:
        logger.info("invalid result:%r", result)
        return

    try:
        props = result.geojson["features"][0]["properties"]
        Event.objects.filter(pk=event.id).update(
            latitude=props["lat"], longitude=props["lng"]
        )
    except (KeyError, IndexError):
        logger.info("bad geocoder data:%s", result.geojson)
