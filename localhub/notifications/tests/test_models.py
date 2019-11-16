# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import pytest
from pywebpush import WebPushException

from localhub.communities.models import Community
from localhub.communities.tests.factories import CommunityFactory, MembershipFactory

from ..models import Notification, PushSubscription
from .factories import NotificationFactory

pytestmark = pytest.mark.django_db


class TestNotificationManager:
    def test_for_community(self, community: Community):

        notification = NotificationFactory(
            community=community, actor=MembershipFactory(community=community).member,
        )
        NotificationFactory(actor=MembershipFactory(community=community).member)
        NotificationFactory(
            actor=MembershipFactory(community=community, active=False).member
        )
        NotificationFactory(
            actor=MembershipFactory(community=CommunityFactory(), active=True).member
        )
        NotificationFactory(community=community)
        NotificationFactory()

        qs = Notification.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == notification


class TestPushSubscriptionModel:
    def test_push_if_ok(self, member, send_notification_webpush_mock):
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

    def test_push_if_timeout(self, member, mocker):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        e = WebPushException("BOOM", response=mocker.Mock(status_code=410))

        with mocker.patch("localhub.notifications.models.webpush", side_effect=e):
            assert not sub.push(payload)

        assert not PushSubscription.objects.exists()
