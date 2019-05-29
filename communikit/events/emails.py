# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from communikit.events.models import EventNotification


def send_notification_email(notification: EventNotification):
    subject = {
        "mentioned": _("You have been mentioned in an event"),
        "created": _("A user has published an event to the %s community")
        % notification.event.community.name,
        "updated": _("A user has edited their event in the %s community")
        % notification.event.community.name,
    }[notification.verb]
    send_mail(
        subject,
        render_to_string(
            "events/emails/notification.txt",
            {
                "notification": notification,
                "event_url": notification.event.get_permalink(),
            },
        ),
        # TBD: need separate email domain setting for commty.
        f"support@{notification.event.community.domain}",
        [notification.recipient.email],
    )
