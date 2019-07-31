# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from django.core.mail import send_mail
from django.template.loader import render_to_string

from localhub.core.types import ContextDict
from localhub.notifications.models import Notification


def send_notification_email(
    notification: Notification,
    subject: str,
    object_url: str,
    plain_template_name: str,
    html_template_name: str,
    extra_context: Optional[ContextDict] = None,
    **kwargs,
):
    context = {
        "subject": subject,
        "object_url": object_url,
        "notification": notification,
    }
    context.update(extra_context or {})
    send_mail(
        subject,
        render_to_string(plain_template_name, context),
        notification.community.resolve_email("no-reply"),
        [notification.recipient.email],
        html_message=render_to_string(html_template_name, context),
        **kwargs,
    )
