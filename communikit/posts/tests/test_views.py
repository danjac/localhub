import pytest

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
