import json
import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils.translation import ugettext as _

from notifications.models import Notification

from communikit.comments.models import Comment
from communikit.communities.models import Community, Membership
from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory
from communikit.likes.models import Like


pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member: Membership) -> Post:
    return PostFactory(author=member.member, community=member.community)


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
    def test_get(self, community: Community, client: Client):
        PostFactory.create_batch(3, community=community)
        response = client.get(reverse("content:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 3

    def test_with_comments(self, comment: Comment, client: Client):
        response = client.get(
            reverse("content:list"), HTTP_HOST=comment.post.community.domain
        )

        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
        assert response.context["object_list"][0].num_comments == 1

    def test_with_likes(
        self, post: Post, user: settings.AUTH_USER_MODEL, client: Client
    ):

        Like.objects.create(content_object=post, user=user)

        response = client.get(
            reverse("content:list"), HTTP_HOST=post.community.domain
        )

        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
        assert response.context["object_list"][0].num_likes == 1


class TestProfilePostListView:
    def test_get(
        self,
        community: Community,
        client: Client,
        user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=user, community=community)
        PostFactory.create_batch(3, community=community, author=user)
        response = client.get(reverse("content:profile", args=[user.username]))
        assert response.status_code == 200
        assert response.context["profile"] == user
        assert len(response.context["object_list"]) == 3

    def test_get_if_not_member(
        self,
        community: Community,
        client: Client,
        user: settings.AUTH_USER_MODEL,
    ):
        response = client.get(reverse("content:profile", args=[user.username]))
        assert response.status_code == 404


class TestPostUpdateView:
    def test_get(self, client: Client, post_for_member: Post):
        response = client.get(
            reverse("content:update", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_post(self, client: Client, post_for_member: Post):
        response = client.post(
            reverse("content:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )
        assert response.url == post_for_member.get_absolute_url()
        post_for_member.refresh_from_db()
        assert post_for_member.title == "UPDATED"


class TestPostDetailView:
    def test_get(self, client: Client, post: Post):
        response = client.get(
            reverse("content:detail", args=[post.id]),
            HTTP_HOST=post.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_post_comment(
        self, client: Client, post: Post, login_user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(member=login_user, community=post.community)
        response = client.get(
            reverse("content:detail", args=[post.id]),
            HTTP_HOST=post.community.domain,
        )
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestPostLikeView:
    def test_if_unliked(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        post.like(member.member)
        response = client.post(
            reverse("content:like", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert json.loads(response.content)["status"] == _("Like")

    def test_if_liked(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("content:like", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert json.loads(response.content)["status"] == _("Unlike")


class TestPostDeleteView:
    def test_get(self, client: Client, post_for_member: Post):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("content:delete", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client: Client, post_for_member: Post):
        response = client.delete(
            reverse("content:delete", args=[post_for_member.id])
        )
        assert response.url == reverse("content:list")
        assert Post.objects.count() == 0

    def test_delete_ajax(self, client: Client, post_for_member: Post):
        response = client.delete(
            reverse("content:delete", args=[post_for_member.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Post.objects.count() == 0


class TestPostSearchView:
    def test_get_for_query(self, client: Client, community: Community):
        PostFactory(community=community, description="random")
        response = client.get(reverse("content:search"), {"q": "random"})
        assert len(response.context["object_list"]) == 1
        assert response.context["search_query"] == "random"

    def test_get_for_hashtag(self, client: Client, community: Community):
        PostFactory(community=community, description="#random")
        response = client.get(reverse("content:search"), {"hashtag": "random"})
        assert len(response.context["object_list"]) == 1
        assert response.context["search_query"] == "#random"


class TestActivityView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        Notification.objects.create(
            actor=post.author,
            recipient=member.member,
            verb="post_created",
            target=member.community,
            action_object=post,
        )
        response = client.get(reverse("content:activity"))
        assert response.status_code == 200
