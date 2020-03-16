# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from celery.utils.log import get_logger
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.notifications.tasks import send_webpush
from localhub.users.utils import user_display

celery_logger = get_logger(__name__)


def send_message_notifications(message):
    send_message_email(message)
    send_message_webpush(message)


def send_message_email(message):

    if message.recipient.send_email_notifications:
        with override(message.recipient.language):
            context = {
                "recipient": message.recipient,
                "message": message,
                "message_url": message.get_permalink(message.recipient),
            }

            if message.parent:
                subject = _("Someone has replied to your message")
            else:
                subject = _("Someone has sent you a message")

            send_mail(
                f"{message.community.name} | {subject}",
                render_to_string("private_messages/emails/message.txt", context),
                message.community.resolve_email("no-reply"),
                [message.recipient.email],
                html_message=render_to_string(
                    "private_messages/emails/message.html", context
                ),
            )


def send_message_webpush(message):
    with override(message.recipient.language):
        payload = {
            "head": _("%(sender)s has sent you a message")
            % {"sender": user_display(message.sender)},
            "body": message.abbreviate(),
            "url": message.get_permalink(message.recipient),
        }
        try:
            return send_webpush.delay(
                message.recipient.id, message.community.id, payload
            )
        except send_webpush.OperationalError as e:
            celery_logger.exception(e)
