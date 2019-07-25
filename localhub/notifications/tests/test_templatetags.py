import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Community, Membership
from localhub.notifications.models import Notification
from localhub.notifications.templatetags.notifications_tags import (
    get_unread_notification_count,
)
from localhub.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestGetUnreadNotificationCount:
    def test_anonymous(self, community: Community):
        assert get_unread_notification_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member: Membership):
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
