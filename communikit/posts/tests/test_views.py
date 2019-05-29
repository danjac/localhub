import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from communikit.communities.models import Community, Membership
from communikit.posts.tests.factories import PostFactory
from communikit.posts.models import Post, PostNotification

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member: Membership) -> Post:
    return PostFactory(owner=member.member, community=member.community)


class TestPostListView:
    def test_get(self, client: Client, community: Community):
        PostFactory.create_batch(3, community=community)
        response = client.get(reverse("posts:list"))
        assert len(response.context["object_list"]) == 3


class TestPostCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("posts:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("posts:create"), {"title": "test", "description": "test"}
        )
        assert response.url == reverse("posts:list")
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


class TestPostLikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("posts:like", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = post.like_set.get()
        assert like.user == member.member


class TestPostDislikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        post.like_set.create(user=member.member)
        response = client.post(
            reverse("posts:dislike", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert post.like_set.count() == 0


class TestPostNotificationMarkReadView:
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
