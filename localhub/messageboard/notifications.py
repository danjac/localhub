# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.messageboard.models import MessageRecipient
from localhub.notifications.utils import send_push_notification


def send_message_notifications(recipient: MessageRecipient):
    send_message_push(recipient)
    send_message_email(recipient)


def send_message_email(recipient: MessageRecipient):

    if recipient.recipient.has_email_pref("new_message"):
        with override(recipient.recipient.language):

            context = {"recipient": recipient, "message": recipient.message}

            send_mail(
                _("%(community)s | Someone has sent you a message")
                % {"community": recipient.message.community.name},
                render_to_string("messageboard/emails/message.txt", context),
                recipient.message.community.resolve_email("no-reply"),
                [recipient.recipient.email],
                html_message=render_to_string(
                    "messageboard/emails/message.html", context
                ),
            )


def send_message_push(recipient: MessageRecipient):
    with override(recipient.recipient.language):
        send_push_notification(
            recipient.recipient,
            recipient.message.community,
            head=_("%(sender)s has sent you a message")
            % {"sender": recipient.message.sender},
            body=recipient.message.subject,
            url=recipient.get_permalink(),
        )
