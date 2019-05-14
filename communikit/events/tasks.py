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
        logger.debug("event not found:%s", event_id)
        return

    if not event.location:
        logger.debug("event does not have location")
        return

    result = geocoder.osm(event.location)
    if not result.ok:
        logger.debug("invalid result:%r", result)
        return

    try:
        props = result.geojson["features"][0]["properties"]
        event.latitude = props["lat"]
        event.longitude = props["lng"]
        event.save()
    except (KeyError, IndexError):
        logger.debug("bad geocoder data:%s", result.geojson)
