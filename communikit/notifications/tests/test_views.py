import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.comments.models import CommentNotification
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.posts.models import PostNotification
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationListView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(activity=post)
        PostNotification.objects.create(post=post, recipient=member.member)
        CommentNotification.objects.create(
            comment=comment, recipient=member.member
        )
        response = client.get(reverse("notifications:list"))
        assert len(response.context["object_list"]) == 2
        assert response.status_code == 200


class TestNotificationMarkReadView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        notification = PostNotification.objects.create(
            post=post, recipient=member.member
        )
        response = client.post(
            reverse("posts:mark_notification_read", args=[notification.id])
        )
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read
