# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from localhub.activities.emails import send_activity_notification_email
from localhub.activities.models import Activity
from localhub.activities.push import send_activity_notification_push
from localhub.notifications.models import Notification

_urlvalidator = URLValidator()


def is_url(url: Optional[str]) -> bool:

    if url is None:
        return False
    try:
        _urlvalidator(url)
    except ValidationError:
        return False
    return True


def get_domain(url: Optional[str]) -> Optional[str]:
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """

    if url is None or not is_url(url):
        return None

    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def send_activity_notifications(
    activity: Activity, notification: Notification
):
    send_activity_notification_push(activity, notification)
    send_activity_notification_email(activity, notification)
