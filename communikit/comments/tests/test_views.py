# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from communikit.comments.models import Comment, Like
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Membership
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

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
        assert comment.owner == member.member


class TestCommentDetailView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(owner=member.member, activity=post)
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.activity.community.domain,
        )
        assert response.status_code == 200


class TestCommentUpdateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(owner=member.member, activity=post)
        response = client.get(reverse("comments:update", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(owner=member.member, activity=post)
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
        comment = CommentFactory(owner=member.member, activity=post)
        response = client.delete(reverse("comments:delete", args=[comment.id]))
        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0


class TestCommentLikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(activity=post)
        response = client.post(
            reverse("comments:like", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = comment.like_set.get()
        assert like.user == member.member


class TestCommentDislikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(activity=post)
        Like.objects.create(user=member.member, comment=comment)
        response = client.post(
            reverse("comments:dislike", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert comment.like_set.count() == 0


class TestCommentProfileView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(activity=post, owner=member.member)
        Like.objects.create(comment=comment, user=UserFactory())
        response = client.get(
            reverse("comments:profile", args=[comment.owner.username])
        )
        assert response.status_code == 200
        assert len(response.context["object_list"]) == 1
        assert response.context["num_likes"] == 1
