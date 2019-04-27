import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Community, Membership
from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory


pytestmark = pytest.mark.django_db


class TestPostCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("content:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("content:create"), {"title": "test", "description": "test"}
        )
        assert response.url == reverse("content:list")
        post = Post.objects.get()
        assert post.author == member.member
        assert post.community == member.community


class TestPostListView:
    def test_get_if_member(self, client: Client, member: Membership):
        PostFactory.create_batch(3, community=member.community)
        response = client.get(reverse("content:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3
        assert "form" in response.context

    def test_get_if_not_member(self, community: Community, client: Client):
        PostFactory.create_batch(3, community=community)
        response = client.get(reverse("content:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3
        assert "form" not in response.context
