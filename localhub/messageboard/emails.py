# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import override

from localhub.messageboard.models import MessageRecipient


def send_message_email(recipient: MessageRecipient):

    if recipient.recipient.has_email_pref("new_message"):
        with override(recipient.recipient.language):

            context = {"recipient": recipient, "message": recipient.message}

            send_mail(
                f"{recipient.message.community.name} | {recipient.message.subject}", # noqa
                render_to_string("messageboard/emails/message.txt", context),
                recipient.message.community.resolve_email("no-reply"),
                [recipient.recipient.email],
                html_message=render_to_string(
                    "messageboard/emails/message.html", context
                ),
            )
