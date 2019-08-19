# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from django.conf import settings

from pywebpush import WebPushException

from pytest_mock import MockFixture

from localhub.notifications.models import PushSubscription

pytestmark = pytest.mark.django_db


class TestPushSubscriptionModel:
    def test_push_if_ok(
        self, user: settings.AUTH_USER_MODEL, mocker: MockFixture
    ):
        sub = PushSubscription.objects.create(
            user=user, endpoint="http://xyz.com", auth="auth", p256dh="xxx"
        )

        payload = {"head": "hello", "body": "testing"}

        with mocker.patch("localhub.notifications.models.webpush"):
            assert sub.push(payload)

        assert PushSubscription.objects.exists()

    def test_push_if_timeout(
        self, user: settings.AUTH_USER_MODEL, mocker: MockFixture
    ):
        sub = PushSubscription.objects.create(
            user=user, endpoint="http://xyz.com", auth="auth", p256dh="xxx"
        )

        payload = {"head": "hello", "body": "testing"}

        e = WebPushException("BOOM", response=mocker.Mock(status_code=410))

        with mocker.patch(
            "localhub.notifications.models.webpush", side_effect=e
        ):
            assert not sub.push(payload)

        assert not PushSubscription.objects.exists()
