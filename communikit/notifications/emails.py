# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string

from communikit.notifications.models import Notification


def send_notification_email(
    notification: Notification,
    subject: str,
    object_url: str,
    template_name: str,
):
    send_mail(
        subject,
        render_to_string(
            template_name,
            {"notification": notification, "object_url": object_url},
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{notification.community.domain}",
        [notification.recipient.email],
    )
