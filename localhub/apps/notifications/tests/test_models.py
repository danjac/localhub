# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from unittest import mock

import pytest
from pywebpush import WebPushException

from localhub.apps.communities.factories import CommunityFactory, MembershipFactory
from localhub.apps.communities.models import Community
from localhub.apps.users.factories import UserFactory

from ..factories import NotificationFactory
from ..models import Notification, PushSubscription

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

    def test_unread_if_read(self):
        NotificationFactory(is_read=True)
        assert Notification.objects.unread().count() == 0

    def test_unread_if_unread(self):
        NotificationFactory(is_read=False)
        assert Notification.objects.unread().count() == 1

    def test_exclude_blocked_actors_if_blocked(self, user):
        other = UserFactory()
        user.blocked.add(other)
        NotificationFactory(actor=other)
        assert Notification.objects.exclude_blocked_actors(user).count() == 0

    def test_exclude_blocked_actors_if_not_blocked(self, user):
        other = UserFactory()
        NotificationFactory(actor=other)
        assert Notification.objects.exclude_blocked_actors(user).count() == 1

    def test_for_recipient(self, user):
        NotificationFactory(recipient=user)
        assert Notification.objects.for_recipient(user).count() == 1


class TestPushSubscriptionModel:
    def test_push_if_ok(self, member):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        with mock.patch("localhub.apps.notifications.models.webpush") as mock_webpush:
            sub.push(payload)
            assert mock_webpush.called_with(
                {
                    "endpoint": sub.endpoint,
                    "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
                },
                payload,
                ttf=0,
            )

        assert PushSubscription.objects.exists()

    def test_push_if_timeout(self, member):
        sub = PushSubscription.objects.create(
            user=member.member,
            community=member.community,
            endpoint="http://xyz.com",
            auth="auth",
            p256dh="xxx",
        )

        payload = {"head": "hello", "body": "testing"}

        e = WebPushException("BOOM", response=mock.Mock(status_code=410))

        with mock.patch("localhub.apps.notifications.models.webpush", side_effect=e):
            assert not sub.push(payload)

        assert not PushSubscription.objects.exists()
