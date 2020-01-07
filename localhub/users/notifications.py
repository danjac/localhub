# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from localhub.notifications.emails import send_notification_email
from localhub.notifications.utils import send_push_notification

from .utils import user_display

NOTIFICATION_HEADERS = {
    "new_follower": _("Someone has started following you"),
    "new_member": _("Someone has just joined this community"),
}

NOTIFICATION_BODY = {
    "new_follower": _("%(user)s has started following you"),
    "new_member": _("%(user)s has just joined this community"),
}


def send_user_notification(user, notification):
    send_user_notification_push(user, notification)
    send_user_notification_email(user, notification)


def send_user_notification_push(user, notification):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            notification.community,
            head=NOTIFICATION_HEADERS[notification.verb],
            body=NOTIFICATION_BODY[notification.verb] % {"user": user_display(user)},
            url=notification.community.resolve_url(user.get_absolute_url()),
        )


def send_user_notification_email(user, notification):

    with override(notification.recipient.language):
        send_notification_email(
            notification,
            NOTIFICATION_HEADERS[notification.verb],
            notification.community.resolve_url(user.get_absolute_url()),
            "users/emails/notification.txt",
            "users/emails/notification.html",
            {"user": user},
        )
