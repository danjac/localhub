# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_notification_email(
    notification,
    subject,
    object_url,
    plain_template_name,
    html_template_name,
    extra_context=None,
    **kwargs,
):
    context = {
        "subject": subject,
        "object_url": object_url,
        "notification": notification,
    }
    context.update(extra_context or {})
    send_mail(
        f"{notification.community.name} | {subject}",
        render_to_string(plain_template_name, context),
        notification.community.resolve_email("no-reply"),
        [notification.recipient.email],
        html_message=render_to_string(html_template_name, context),
        **kwargs,
    )
