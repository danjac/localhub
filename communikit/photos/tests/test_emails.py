# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List, Any

from django.conf import settings

from communikit.photos.emails import send_notification_email
from communikit.photos.models import Photo, PhotoNotification

pytestmark = pytest.mark.django_db


class TestSendNotificationEmail:
    def test_send_if_created(
        self,
        user: settings.AUTH_USER_MODEL,
        photo: Photo,
        mailoutbox: List[Any],
    ):

        notification = PhotoNotification.objects.create(
            photo=photo, recipient=user, verb="created"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has published an photo to the {photo.community.name} community"  # noqa
        )
        assert (
            f"User {photo.owner.username} has published an photo" in mail.body
        )

    def test_send_if_updated(
        self,
        user: settings.AUTH_USER_MODEL,
        photo: Photo,
        mailoutbox: List[Any],
    ):

        notification = PhotoNotification.objects.create(
            photo=photo, recipient=user, verb="updated"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has edited their photo in the {photo.community.name} community"  # noqa
        )
        assert f"User {photo.owner.username} has edited an photo" in mail.body
