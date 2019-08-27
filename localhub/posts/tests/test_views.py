# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.urls import reverse

from localhub.comments.models import Comment
from localhub.communities.models import Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification
from localhub.posts.tests.factories import PostFactory
from localhub.posts.models import Post

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member):
    return PostFactory(owner=member.member, community=member.community)


class TestPostListView:
    def test_get_if_anonymous(self, client, member):
        PostFactory.create_batch(
            3, community=member.community, owner=member.member
        )
        response = client.get(reverse("posts:list"))
        assert len(response.context["object_list"]) == 3

    def test_search(self, client, member):
        PostFactory.create_batch(
            3, community=member.community, owner=member.member, title="testme"
        )
        for post in Post.objects.all():
            post.search_indexer.update()

        response = client.get(reverse("posts:list"), {"q": "testme"})
        assert len(response.context["object_list"]) == 3


class TestPostCreateView:
    def test_get(self, client, member):
        response = client.get(reverse("posts:create"))
        assert response.status_code == 200

    def test_post(self, client, member, send_notification_webpush_mock):
        response = client.post(
            reverse("posts:create"), {"title": "test", "description": "test"}
        )
        post = Post.objects.get()
        assert response.url == post.get_absolute_url()
        assert post.owner == member.member
        assert post.community == member.community


class TestPostUpdateView:
    def test_get(self, client, post_for_member):
        response = client.get(
            reverse("posts:update", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_post(
        self, client, post_for_member, send_notification_webpush_mock
    ):
        response = client.post(
            reverse("posts:update", args=[post_for_member.id]),
            {"title": "UPDATED", "description": post_for_member.description},
        )
        post_for_member.refresh_from_db()
        assert response.url == post_for_member.get_absolute_url()
        assert post_for_member.title == "UPDATED"

    def test_post_moderator(
        self, client, moderator, send_notification_webpush_mock
    ):
        post = PostFactory(
            community=moderator.community,
            owner=MembershipFactory(community=moderator.community).member,
        )
        response = client.post(
            reverse("posts:update", args=[post.id]),
            {"title": "UPDATED", "description": post.description},
        )
        post.refresh_from_db()
        assert response.url == post.get_absolute_url()
        assert post.title == "UPDATED"
        assert post.editor == moderator.member


class TestPostCommentCreateView:
    def test_get(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("posts:comment", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_notification_webpush_mock):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("posts:comment", args=[post.id]), {"content": "test"}
        )
        assert response.url == post.get_absolute_url()
        comment = Comment.objects.get()
        assert comment.owner == member.member
        assert comment.content_object == post

        notification = Notification.objects.get(
            recipient=post.owner, comment=comment
        )
        assert notification.verb == "new_comment"


class TestPostDeleteView:
    def test_get(self, client, post_for_member: Post):
        # test confirmation page for non-JS clients
        response = client.get(
            reverse("posts:delete", args=[post_for_member.id])
        )
        assert response.status_code == 200

    def test_delete(self, client, post_for_member: Post):
        response = client.delete(
            reverse("posts:delete", args=[post_for_member.id])
        )
        assert response.url == reverse("activities:stream")
        assert Post.objects.count() == 0

    def test_delete_by_moderator(self, client, moderator):
        post = PostFactory(
            community=moderator.community,
            owner=MembershipFactory(community=moderator.community).member,
        )
        response = client.delete(reverse("posts:delete", args=[post.id]))
        assert response.url == reverse("activities:stream")
        assert Post.objects.count() == 0


class TestPostDetailView:
    def test_get(self, client, post):
        response = client.get(
            post.get_absolute_url(), HTTP_HOST=post.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_post_comment(self, client, post, login_user):
        MembershipFactory(member=login_user, community=post.community)
        response = client.get(
            post.get_absolute_url(), HTTP_HOST=post.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" in response.context


class TestPostReshareView:
    def test_post(self, client, member, send_notification_webpush_mock):

        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("posts:reshare", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.url == post.get_absolute_url()
        assert post.reshares.filter(owner=member.member).count() == 1
        assert (
            Notification.objects.filter(
                actor=member.member, recipient=post.owner, verb="reshare"
            ).count()
            == 1
        )


class TestPostLikeView:
    def test_post(self, client, member, send_notification_webpush_mock):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("posts:like", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = Like.objects.get()
        assert like.user == member.member

        assert send_notification_webpush_mock.called_once()


class TestPostDislikeView:
    def test_post(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        Like.objects.create(
            user=member.member,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        response = client.post(
            reverse("posts:dislike", args=[post.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Like.objects.count() == 0


class TestFlagView:
    def test_get(self, client, member):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("posts:flag", args=[post.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_notification_webpush_mock):
        post = PostFactory(
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        moderator = MembershipFactory(
            community=post.community, role=Membership.ROLES.moderator
        )
        response = client.post(
            reverse("posts:flag", args=[post.id]), data={"reason": "spam"}
        )
        assert response.url == post.get_absolute_url()

        flag = Flag.objects.get()
        assert flag.user == member.member

        notification = Notification.objects.get()
        assert notification.recipient == moderator.member
