# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification

NOTIFICATION_PREFERENCES = {"subscribe": "subscribes"}

NOTIFICATION_SUBJECTS = {"subscribe": _("Someone has started following you")}


def send_user_notification_email(
    user: settings.AUTH_USER_MODEL, notification: Notification
):

    if notification.recipient.has_email_pref(
        NOTIFICATION_PREFERENCES[notification.verb]
    ):
        send_notification_email(
            notification,
            NOTIFICATION_SUBJECTS[notification.verb],
            notification.community.resolve_url(user.get_absolute_url()),
            "users/emails/notification.txt",
            "users/emails/notification.html",
            {"user": user},
        )
