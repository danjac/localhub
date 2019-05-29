import pytest

from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from communikit.comments.models import CommentNotification
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.notifications.templatetags.notifications_tags import (
    get_unread_notifications_count,
)
from communikit.events.tests.factories import EventFactory
from communikit.events.models import EventNotification
from communikit.posts.models import PostNotification
from communikit.posts.tests.factories import PostFactory

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
        comment = CommentFactory(activity=post)
        event = EventFactory(community=member.community)

        PostNotification.objects.create(post=post, recipient=member.member)
        EventNotification.objects.create(event=event, recipient=member.member)

        CommentNotification.objects.create(
            comment=comment, recipient=member.member
        )
        # discount read notifications
        CommentNotification.objects.create(
            comment=comment, recipient=member.member, is_read=True
        )
        request = req_factory.get("/")
        request.user = member.member
        request.community = member.community
        assert get_unread_notifications_count({"request": request}) == 3
