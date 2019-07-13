# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string

from localite.messageboard.models import MessageRecipient


def send_message_email(recipient: MessageRecipient):

    send_mail(
        recipient.message.subject,
        render_to_string(
            "messageboard/emails/message.txt",
            {"recipient": recipient, "message": recipient.message},
        ),
        recipient.message.community.resolve_email("messages"),
        [recipient.recipient.email],
    )
