# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from celery import shared_task
from celery.utils.log import get_task_logger

# Local
from .models import PushSubscription

logger = get_task_logger(__name__)


@shared_task(name="social_bfg.notifications.send_webpush")
def send_webpush(recipient_id, community_id, payload):
    for subscription in PushSubscription.objects.filter(
        user__pk=recipient_id, community__pk=community_id
    ):
        try:
            if subscription.push(payload):
                logger.info("Notification push sent")
        except Exception as e:
            logger.exception(e)
