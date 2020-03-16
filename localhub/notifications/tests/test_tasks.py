# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..models import PushSubscription
from ..tasks import send_webpush

pytestmark = pytest.mark.django_db


class TestSendPushNotification:
    def test_send_ok(self, member, send_webpush_mock):

        PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        send_webpush(member.member_id, member.community_id, payload)
        assert send_webpush_mock.called_once()
