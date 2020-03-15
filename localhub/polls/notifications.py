# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.utils.translation import gettext as _
from django.utils.translation import override
from django.utils.encoding import force_text

from localhub.notifications.emails import send_notification_email
from localhub.notifications.utils import send_push_notification
from localhub.users.utils import user_display


def send_vote_notification(poll, notification):
    with override(notification.recipient.language):
        header = _("%(actor)s has voted on this poll") % {
            "actor": user_display(notification.actor)
        }
        send_vote_notification_push(poll, header, notification)
        send_vote_notification_email(poll, header, notification)


def send_vote_notification_push(poll, header, notification):
    with override(notification.recipient.language):

        send_push_notification(
            notification.recipient,
            notification.community,
            head=header,
            body=force_text(poll),
            url=poll.get_permalink(),
        )


def send_vote_notification_email(poll, header, notification):
    send_notification_email(
        notification,
        header,
        poll.get_permalink(),
        "polls/emails/notifications/vote.txt",
        "polls/emails/notifications/vote.html",
        {"activity_name": "poll"},
    )
