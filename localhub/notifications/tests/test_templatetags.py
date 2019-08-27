import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.notifications.models import Notification
from localhub.notifications.templatetags.notifications_tags import (
    get_unread_notification_count,
    notifications_subscribe_btn,
)
from localhub.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationsSubscribeBtn:
    def test_authenticated(self, member):

        assert notifications_subscribe_btn(
            member.member, member.community
        ) == {
            "user": member.member,
            "community": member.community,
            "vapid_public_key": None,
        }


class TestGetUnreadNotificationCount:
    def test_anonymous(self, community):
        assert get_unread_notification_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member):
        post = PostFactory(community=member.community)

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
            get_unread_notification_count(member.member, member.community) == 1
        )
