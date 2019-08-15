# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification


NOTIFICATION_SUBJECTS = {
    "new_follower": _("Someone has started following you"),
    "new_member": _("Someone has just joined this community"),
}


def send_user_notification_email(
    user: settings.AUTH_USER_MODEL, notification: Notification
):

    if notification.recipient.has_email_pref(notification.verb):
        with override(notification.recipient.language):
            send_notification_email(
                notification,
                NOTIFICATION_SUBJECTS[notification.verb],
                notification.community.resolve_url(user.get_absolute_url()),
                "users/emails/notification.txt",
                "users/emails/notification.html",
                {"user": user},
            )
