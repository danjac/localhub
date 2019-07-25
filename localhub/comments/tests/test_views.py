# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.test.client import Client
from django.urls import reverse

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Membership
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestCommentDetailView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(owner=member.member, content_object=post)
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.community.domain,
        )
        assert response.status_code == 200


class TestCommentUpdateView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member,
            content_object=post,
            community=member.community,
        )
        response = client.get(reverse("comments:update", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member,
            content_object=post,
            community=member.community,
        )
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
        comment = CommentFactory(
            owner=member.member,
            content_object=post,
            community=member.community,
        )
        response = client.delete(reverse("comments:delete", args=[comment.id]))
        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0

    def test_delete_by_moderator(self, client: Client, moderator: Membership):
        post = PostFactory(community=moderator.community)
        comment = CommentFactory(
            owner=UserFactory(),
            content_object=post,
            community=moderator.community,
        )
        response = client.delete(reverse("comments:delete", args=[comment.id]))

        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0


class TestCommentLikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, community=member.community
        )
        response = client.post(
            reverse("comments:like", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = Like.objects.get()
        assert like.user == member.member


class TestCommentDislikeView:
    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, community=member.community
        )
        Like.objects.create(
            user=member.member,
            content_object=comment,
            community=comment.community,
            recipient=comment.owner,
        )
        response = client.post(
            reverse("comments:dislike", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        assert Like.objects.count() == 0


class TestFlagView:
    def test_get(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, community=member.community
        )
        response = client.get(reverse("comments:flag", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client: Client, member: Membership):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post, community=member.community
        )
        moderator = Membership.objects.create(
            member=UserFactory(),
            community=post.community,
            role=Membership.ROLES.moderator,
        )
        response = client.post(
            reverse("comments:flag", args=[comment.id]),
            data={"reason": "spam"},
        )
        assert response.url == post.get_absolute_url()

        flag = Flag.objects.get()
        assert flag.user == member.member

        notification = Notification.objects.get(recipient=moderator.member)
        assert notification.verb == "flag"
