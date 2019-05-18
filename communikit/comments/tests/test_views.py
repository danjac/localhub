import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text

from communikit.comments.models import Comment
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Community, Membership
from communikit.posts.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestCommentCreateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.get(reverse("comments:create", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("comments:create", args=[post.id]), {"content": "test"}
        )
        assert response.url == post.get_absolute_url()
        comment = post.comment_set.get()
        assert comment.author == member.member


class TestCommentDetailView:
    def test_get(self, client: Client, comment: Comment):
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.post.community.domain,
        )
        assert response.status_code == 200


class TestCommentUpdateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.get(reverse("comments:update", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.post(
            reverse("comments:update", args=[comment.id]),
            {"content": "new content"},
        )
        assert response.url == post.get_absolute_url()
        comment.refresh_from_db()
        assert comment.content == "new content"


class TestCommentDeleteView:
    def test_delete(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(author=member.member, post=post)
        response = client.delete(reverse("comments:delete", args=[comment.id]))
        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0


class TestProfileCommentListView:
    def test_get(
        self,
        community: Community,
        client: Client,
        user: settings.AUTH_USER_MODEL,
    ):
        Membership.objects.create(member=user, community=community)
        post = PostFactory(community=community)
        CommentFactory.create_batch(3, post=post, author=user)
        response = client.get(
            reverse("comments:profile", args=[user.username])
        )
        assert response.status_code == 200
        assert response.context["profile"] == user
        assert len(response.context["object_list"]) == 3

    def test_get_if_not_member(
        self,
        community: Community,
        client: Client,
        user: settings.AUTH_USER_MODEL,
    ):
        response = client.get(
            reverse("comments:profile", args=[user.username])
        )
        assert response.status_code == 404


class TestCommentLikeView:
    def test_if_unliked(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(post=post)
        comment.like(member.member)
        response = client.post(
            reverse("comments:like", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert smart_text(response.content) == _("Like")

    def test_if_liked(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(post=post)
        response = client.post(
            reverse("comments:like", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert smart_text(response.content) == _("Unlike")
