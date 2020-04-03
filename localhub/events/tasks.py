# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Event

logger = get_task_logger(__name__)


@shared_task(name="events.update_event_coordinates")
def update_event_coordinates(event_id):
    try:
        Event.objects.get(pk=event_id).update_coordinates()
    except Event.DoesNotExist:
        logger.info("event not found:%s", event_id)
