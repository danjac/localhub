# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Dict

from celery import shared_task

from celery.utils.log import get_task_logger


from localhub.notifications.models import PushSubscription

logger = get_task_logger(__name__)


@shared_task(name="notifications.send_push_notification")
def send_push_notification(recipient_id: int, payload: Dict[str, Any]):
    for subscription in PushSubscription.objects.filter(user__pk=recipient_id):
        try:
            if subscription.push(payload):
                logger.log("Notification push sent")
        except Exception as e:
            logger.exception(e)
