# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.defaultfilters import truncatechars, striptags
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.conversations.models import Message
from localhub.notifications.utils import send_push_notification


def send_message_notifications(message: Message):
    send_message_push(message)
    send_message_email(message)


def send_message_email(message: Message):

    if message.recipient.has_email_pref("new_message"):
        with override(message.recipient.language):

            context = {"recipient": message.recipient, "message": message}

            send_mail(
                _("%(community)s | Someone has sent you a message")
                % {"community": message.community.name},
                render_to_string("conversations/emails/message.txt", context),
                message.community.resolve_email("no-reply"),
                [message.recipient.email],
                html_message=render_to_string(
                    "conversations/emails/message.html", context
                ),
            )


def send_message_push(message: Message):
    with override(message.recipient.language):
        send_push_notification(
            message.recipient,
            message.community,
            head=_("%(sender)s has sent you a message")
            % {"sender": message.sender},
            body=truncatechars(striptags(message.message.markdown()), 60),
            url=message.get_permalink(),
        )
