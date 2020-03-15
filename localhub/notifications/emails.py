# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import override


def send_notification_email(
    notification, extra_context=None, **kwargs,
):

    if notification.recipient.send_email_notifications:

        with override(notification.recipient.language):
            subject = notification.get_header()

            context = {
                "subject": subject,
                "object_url": notification.community.resolve_url(
                    notification.get_object_url()
                ),
                "notification": notification,
            }
            context.update(notification.get_email_context())
            send_mail(
                f"{notification.community.name} | {subject}",
                render_to_string(notification.get_plain_email_template(), context),
                notification.community.resolve_email("no-reply"),
                [notification.recipient.email],
                html_message=render_to_string(
                    notification.get_html_email_template(), context,
                ),
                **kwargs,
            )
