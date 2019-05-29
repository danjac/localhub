# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from communikit.photos.models import PhotoNotification


def send_notification_email(notification: PhotoNotification):
    subject = {
        "created": _("A user has published an photo to the %s community")
        % notification.photo.community.name,
        "updated": _("A user has edited their photo in the %s community")
        % notification.photo.community.name,
    }[notification.verb]
    send_mail(
        subject,
        render_to_string(
            "photos/emails/notification.txt",
            {
                "notification": notification,
                "photo_url": notification.photo.get_permalink(),
            },
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{notification.photo.community.domain}",
        [notification.recipient.email],
    )
