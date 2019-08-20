# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

from localhub.communities.models import Community
from localhub.notifications import tasks


def send_push_notification(
    recipient: settings.AUTH_USER_MODEL,
    community: Community,
    head: str,
    body: str,
    url: str,
    icon: str = "",
):
    payload = {"head": head, "body": body, "url": url}
    if icon:
        payload["icon"] = icon

    return tasks.send_push_notification.delay(
        recipient.id, community.id, payload
    )
