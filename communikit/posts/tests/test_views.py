import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Membership
from communikit.posts.tests.factories import PostFactory
from communikit.posts.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member: Membership) -> Post:
    return PostFactory(owner=member.member, community=member.community)


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


class TestPostUpdateView:
    def test_get(self, client: Client, post_for_member: Post):
        response = client.get(
            reverse("posts:update", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_post(self, client: Client, post_for_member: Post):
        response = client.post(
            reverse("posts:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )
        assert response.url == post_for_member.get_absolute_url()
        post_for_member.refresh_from_db()
        assert post_for_member.title == "UPDATED"


class TestPostDeleteView:
    def test_get(self, client: Client, post_for_member: Post):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("posts:delete", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client: Client, post_for_member: Post):
        response = client.delete(
            reverse("posts:delete", args=[post_for_member.id])
        )
        assert response.url == reverse("activities:stream")
        assert Post.objects.count() == 0


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
