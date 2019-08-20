# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from pytest_mock import MockFixture

from localhub.communities.models import Membership
from localhub.notifications.models import PushSubscription
from localhub.notifications.tasks import send_push_notification

pytestmark = pytest.mark.django_db


class TestSendPushNotification:
    def test_send_ok(
        self, member: Membership, send_notification_webpush_mock: MockFixture
    ):

        PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        send_push_notification(member.member_id, member.community_id, payload)
        assert send_notification_webpush_mock.called_once()
