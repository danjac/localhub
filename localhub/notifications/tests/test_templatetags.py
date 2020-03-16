# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser
from django.template import engines

from localhub.communities.factories import MembershipFactory
from localhub.posts.factories import PostFactory

from ..factories import NotificationFactory
from ..models import Notification
from ..templatetags.notifications_tags import (
    get_unread_external_notification_count,
    get_unread_notification_count,
    notifications_subscribe_btn,
)

pytestmark = pytest.mark.django_db


class TestRenderNotification:
    def test_render_notification(self, post):
        notification = NotificationFactory(
            content_object=post,
            verb="mention",
            actor=post.owner,
            community=post.community,
        )

        tmpl = engines["django"].from_string(
            """
        {% load notifications_tags %}
        {% render_notification notification %}
        """
        )
        response = tmpl.render({"notification": notification})
        assert "has mentioned" in response


class TestNotificationsSubscribeBtn:
    def test_authenticated(self, member):

        assert notifications_subscribe_btn(member.member, member.community) == {
            "user": member.member,
            "community": member.community,
            "vapid_public_key": None,
        }


class TestGetUnreadNotificationCount:
    def test_anonymous(self, community):
        assert get_unread_notification_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )

        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="updated",
            is_read=False,
        )

        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="updated",
            is_read=True,
        )

        assert get_unread_notification_count(member.member, member.community) == 1


class TestGetUnreadLocalNetworkNotificationCount:
    def test_anonymous(self, community):
        assert get_unread_external_notification_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member):

        other = MembershipFactory(member=member.member).community

        post = PostFactory(
            community=other, owner=MembershipFactory(community=other).member
        )

        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="updated",
            is_read=False,
        )

        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="updated",
            is_read=True,
        )

        assert (
            get_unread_external_notification_count(member.member, member.community) == 1
        )
