# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List, Any

from django.conf import settings

from communikit.events.emails import send_notification_email
from communikit.events.models import Event, EventNotification

pytestmark = pytest.mark.django_db


class TestSendNotificationEmail:
    def test_send_if_mentioned(
        self,
        user: settings.AUTH_USER_MODEL,
        event: Event,
        mailoutbox: List[Any],
    ):

        notification = EventNotification.objects.create(
            event=event, recipient=user, verb="mentioned"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == "You have been mentioned in an event"
        assert (
            f"User {event.owner.username} has mentioned you in an event"
            in mail.body
        )

    def test_send_if_created(
        self,
        user: settings.AUTH_USER_MODEL,
        event: Event,
        mailoutbox: List[Any],
    ):

        notification = EventNotification.objects.create(
            event=event, recipient=user, verb="created"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has published an event to the {event.community.name} community"  # noqa
        )
        assert (
            f"User {event.owner.username} has published an event" in mail.body
        )

    def test_send_if_updated(
        self,
        user: settings.AUTH_USER_MODEL,
        event: Event,
        mailoutbox: List[Any],
    ):

        notification = EventNotification.objects.create(
            event=event, recipient=user, verb="updated"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has edited their event in the {event.community.name} community"  # noqa
        )
        assert f"User {event.owner.username} has edited an event" in mail.body
