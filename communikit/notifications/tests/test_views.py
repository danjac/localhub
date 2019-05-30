import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership
from communikit.notifications.models import Notification
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestNotificationListView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.get(reverse("notifications:list"))
        assert len(response.context["object_list"]) == 1
        assert response.status_code == 200


class TestNotificationMarkReadView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        notification = Notification.objects.create(
            content_object=post,
            recipient=member.member,
            actor=post.owner,
            community=post.community,
            verb="created",
        )
        response = client.post(
            reverse(
                "notifications:mark_notification_read", args=[notification.id]
            )
        )
        assert response.url == reverse("notifications:list")
        notification.refresh_from_db()
        assert notification.is_read
