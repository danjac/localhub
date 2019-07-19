# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import Callable

from django.core import mail
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from localhub.comments.models import Comment
from localhub.communities.models import Community, Membership
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification
from localhub.posts.tests.factories import PostFactory
from localhub.posts.models import Post
from localhub.subscriptions.models import Subscription
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_for_member(member: Membership) -> Post:
    return PostFactory(owner=member.member, community=member.community)


class TestPostListView:
    def test_get_if_anonymous(self, client: Client, community: Community):
        PostFactory.create_batch(3, community=community)
        response = client.get(reverse("posts:list"))
        assert len(response.context["object_list"]) == 3

    def test_get_if_authenticated_following(
        self, client: Client, member: Membership
    ):

        PostFactory(owner=member.member, community=member.community)
        post = PostFactory(community=member.community)

        Subscription.objects.create(
            subscriber=member.member,
            community=member.community,
            content_object=post.owner,
        )
        response = client.get(reverse("posts:list"), {"following": "1"})
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2

    def test_get_if_authenticated_show_all(
        self, client: Client, member: Membership
    ):

        PostFactory(owner=member.member, community=member.community)
        PostFactory(community=member.community)
        response = client.get(reverse("posts:list"))
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 2


class TestPostCreateView:
    def test_get(self, client: Client, member: Membership):
        response = client.get(reverse("posts:create"))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        response = client.post(
            reverse("posts:create"), {"title": "test", "description": "test"}
        )
        post = Post.objects.get()
        assert response.url == post.get_absolute_url()
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
        post_for_member.refresh_from_db()
        assert response.url == post_for_member.get_absolute_url()
        assert post_for_member.title == "UPDATED"

    def test_post_moderator(self, client: Client, moderator: Membership):
        post = PostFactory(community=moderator.community)
        response = client.post(
            reverse("posts:update", args=[post.id]),
            {"title": "UPDATED", "description": post.description},
        )
        post.refresh_from_db()
        assert response.url == post.get_absolute_url()
        assert post.title == "UPDATED"
        assert post.editor == moderator.member


class TestPostCommentCreateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.get(reverse("posts:comment", args=[post.id]))
        assert response.status_code == 200

    def test_post(
        self, client: Client, member: Membership, transactional_db: Callable
    ):
        post = PostFactory(community=member.community)
        response = client.post(
            reverse("posts:comment", args=[post.id]), {"content": "test"}
        )
        assert response.url == post.get_absolute_url()
        comment = Comment.objects.get()
        assert comment.owner == member.member
        assert comment.content_object == post

        notification = Notification.objects.get(recipient=post.owner)
        assert notification.verb == "commented"

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == post.owner.email


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
            post.get_absolute_url(), HTTP_HOST=post.community.domain
        )
        assert response.status_code == 200
        assert "comment_form" not in response.context

    def test_get_if_can_post_comment(
        self, client: Client, post: Post, login_user: settings.AUTH_USER_MODEL
    ):
        Membership.objects.create(member=login_user, community=post.community)
        response = client.get(
            post.get_absolute_url(), HTTP_HOST=post.community.domain
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
        like = Like.objects.get()
        assert like.user == member.member


class TestPostDislikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
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
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        response = client.get(reverse("posts:flag", args=[post.id]))
        assert response.status_code == 200

    def test_post(
        self, client: Client, member: Membership, transactional_db: Callable
    ):
        post = PostFactory(community=member.community)
        moderator = Membership.objects.create(
            member=UserFactory(),
            community=post.community,
            role=Membership.ROLES.moderator,
        )
        response = client.post(
            reverse("posts:flag", args=[post.id]), data={"reason": "spam"}
        )
        assert response.url == post.get_absolute_url()

        flag = Flag.objects.get()
        assert flag.user == member.member

        notification = Notification.objects.get()
        assert notification.recipient == moderator.member

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == moderator.member.email
