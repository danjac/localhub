# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery.utils.log import get_logger
from django.utils.encoding import force_text
from django.utils.translation import override

from .tasks import send_webpush

celery_logger = get_logger(__name__)


def send_notification_webpush(notification):
    with override(notification.recipient.language):
        payload = {
            "head": notification.get_header(),
            "body": force_text(notification.content_object),
            "url": notification.community.resolve_url(notification.get_object_url()),
        }

        # TBD: add notification logo or actor avatar
        # if icon:
        #    payload["icon"] = icon
        return send_webpush_task(
            notification.recipient_id, notification.community_id, payload
        )


def send_webpush_task(user_id, community_id, payload):
    """
    Wraps webpush task call
    """
    try:
        return send_webpush.delay(user_id, community_id, payload)
    except send_webpush.OperationalError as e:
        celery_logger.exception(e)
