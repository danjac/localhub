import pytest

from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from localite.communities.models import Membership
from localite.notifications.models import Notification
from localite.notifications.templatetags.notifications_tags import (
    get_unread_notifications_count,
)
from localite.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestGetUnreadNotificationsCount:
    def test_anonymous(self, req_factory: RequestFactory):
        request = req_factory.get("/")
        request.user = AnonymousUser()
        assert get_unread_notifications_count({"request": request}) == 0

    def test_authenticated(
        self, req_factory: RequestFactory, member: Membership
    ):
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

        request = req_factory.get("/")
        request.user = member.member
        request.community = member.community
        assert get_unread_notifications_count({"request": request}) == 1
