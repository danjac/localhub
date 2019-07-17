# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.activities.models import Activity
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification

SUBJECTS = {
    "mentioned": _("Someone has mentioned you in their %s"),
    "created": _("Someone has published a new %s"),
    "updated": _("Someone has updated their %s"),
    "flagged": _("Someone has flagged this %s"),
    "tagged": _("Someone has published a new %s you might be interested in"),
}


def send_activity_notification_email(
    activity: Activity, notification: Notification
):

    activity_name = activity._meta.verbose_name

    send_notification_email(
        notification,
        SUBJECTS[notification.verb] % activity_name,
        activity.get_permalink(),
        "activities/emails/notification.txt",
        "activities/emails/notification.html",
        {"activity_name": activity_name},
    )
