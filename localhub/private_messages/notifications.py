# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.notifications.utils import send_push_notification
from localhub.users.utils import user_display


def send_message_notifications(message):
    send_message_push(message)
    send_message_email(message)


def send_message_email(message):

    if message.recipient.has_email_pref("new_message"):
        with override(message.recipient.language):

            context = {"recipient": message.recipient, "message": message}

            if message.parent:
                subject = _("Someone has replied to your message")
            else:
                subject = _("Someone has sent you a message")

            send_mail(
                f"{message.community.name} | {subject}",
                render_to_string(
                    "private_messages/emails/message.txt", context
                ),
                message.community.resolve_email("no-reply"),
                [message.recipient.email],
                html_message=render_to_string(
                    "private_messages/emails/message.html", context
                ),
            )


def send_message_push(message):
    with override(message.recipient.language):

        send_push_notification(
            message.recipient,
            message.community,
            head=_("%(sender)s has sent you a message")
            % {"sender": user_display(message.sender)},
            body=message.get_abbreviation(),
            url=message.get_permalink(),
        )
