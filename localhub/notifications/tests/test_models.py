# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest

from pywebpush import WebPushException

from pytest_mock import MockFixture

from localhub.communities.models import Membership
from localhub.notifications.models import PushSubscription

pytestmark = pytest.mark.django_db


class TestPushSubscriptionModel:
    def test_push_if_ok(
        self, member: Membership, send_notification_webpush_mock: MockFixture
    ):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        assert sub.push(payload)
        assert send_notification_webpush_mock.called_with(
            {
                "endpoint": sub.endpoint,
                "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
            },
            payload,
            ttf=0,
        )

        assert PushSubscription.objects.exists()

    def test_push_if_timeout(self, member: Membership, mocker: MockFixture):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        e = WebPushException("BOOM", response=mocker.Mock(status_code=410))

        with mocker.patch(
            "localhub.notifications.models.webpush", side_effect=e
        ):
            assert not sub.push(payload)

        assert not PushSubscription.objects.exists()
