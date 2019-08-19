# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings

from pytest_mock import MockFixture

from localhub.notifications.models import PushSubscription
from localhub.notifications.tasks import send_push_notification

pytestmark = pytest.mark.django_db


class TestSendPushNotification:
    def test_send_ok(
        self, user: settings.AUTH_USER_MODEL, mocker: MockFixture
    ):

        PushSubscription.objects.create(
            user=user, endpoint="http://xyz.com", auth="auth", p256dh="xxx"
        )

        payload = {"head": "hello", "body": "testing"}

        with mocker.patch("localhub.notifications.models.webpush"):
            send_push_notification(user.id, payload)
