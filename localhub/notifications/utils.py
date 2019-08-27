# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from celery.utils.log import get_logger

from localhub.notifications import tasks

celery_logger = get_logger(__name__)


def send_push_notification(recipient, community, head, body, url, icon=""):
    payload = {"head": head, "body": body, "url": url}
    if icon:
        payload["icon"] = icon

    try:
        return tasks.send_push_notification.delay(
            recipient.id, community.id, payload
        )
    except tasks.send_push_notification.OperationalError as e:
        celery_logger.exception(e)
