from celery import shared_task
from celery.utils.log import get_task_logger

from communikit.events.models import Event

logger = get_task_logger(__name__)


@shared_task
def update_event_coordinates(event_id: int):
    try:
        event = Event.objects.get(pk=event_id)
        event.update_coordinates()
    except Event.DoesNotExist:
        logger.info("event not found:%s", event_id)
