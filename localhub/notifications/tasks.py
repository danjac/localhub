# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from celery import shared_task
from celery.utils.log import get_task_logger

from .models import PushSubscription

logger = get_task_logger(__name__)


@shared_task(name="notifications.send_push_notification")
def send_push_notification(recipient_id, community_id, payload):
    for subscription in PushSubscription.objects.filter(
        user__pk=recipient_id, community__pk=community_id
    ):
        try:
            if subscription.push(payload):
                logger.info("Notification push sent")
        except Exception as e:
            logger.exception(e)
