import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership
from communikit.posts.models import Post

pytestmark = pytest.mark.django_db


class TestPostCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("posts:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("posts:create"), {"title": "test", "description": "test"}
        )
        assert response.url == reverse("activities:stream")
        post = Post.objects.get()
        assert post.owner == member.member
        assert post.community == member.community


class TestPostDetailView:
    def test_get(self, client: Client, post: Post):
        response = client.get(
            reverse("posts:detail", args=[post.id]),
            HTTP_HOST=post.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_post_comment(
        self, client: Client, post: Post, login_user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(member=login_user, community=post.community)
        response = client.get(
            reverse("posts:detail", args=[post.id]),
            HTTP_HOST=post.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" in response.context
