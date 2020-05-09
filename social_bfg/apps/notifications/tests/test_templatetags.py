# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.template import engines

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.communities.factories import MembershipFactory
from social_bfg.apps.posts.factories import PostFactory

# Local
from ..factories import NotificationFactory
from ..models import Notification
from ..templatetags.notifications import (
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
        {% load notifications %}
        {% notification notification %}
        <div class="notification">
        {{ notification_content }}
        </div>
        {% endnotification %}
        """
        )
        response = tmpl.render({"notification": notification})
        assert 'div class="notification"' in response
        assert "has mentioned" in response

    def test_render_notification_if_not_allowed(self, post):
        notification = NotificationFactory(
            content_object=post,
            verb="not_allowed",
            actor=post.owner,
            community=post.community,
        )

        tmpl = engines["django"].from_string(
            """
        {% load notifications %}
        {% notification notification %}
        <div class="notification">
        {{ notification_content }}
        </div>
        {% endnotification %}
        """
        )
        response = tmpl.render({"notification": notification}).strip()
        assert response == ""


class TestNotificationsSubscribeBtn:
    def test_authenticated(self, member, settings):

        settings.SOCIAL_BFG_WEBPUSH_ENABLED = True
        assert notifications_subscribe_btn(member.member, member.community) == {
            "user": member.member,
            "community": member.community,
            "vapid_public_key": None,
            "webpush_enabled": True,
        }

    def test_webpush_disabled(self, member, settings):

        settings.SOCIAL_BFG_WEBPUSH_ENABLED = False
        assert notifications_subscribe_btn(member.member, member.community) == {
            "user": member.member,
            "community": member.community,
            "vapid_public_key": None,
            "webpush_enabled": False,
        }


class TestGetUnreadNotificationCount:
    def test_anonymous(self, community, anonymous_user):
        assert get_unread_notification_count(anonymous_user, community) == 0

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
    def test_anonymous(self, community, anonymous_user):
        assert get_unread_external_notification_count(anonymous_user, community) == 0

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
