# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership
from localhub.flags.models import Flag
from localhub.likes.factories import LikeFactory
from localhub.likes.models import Like
from localhub.notifications.factories import NotificationFactory
from localhub.notifications.models import Notification
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

from ..factories import CommentFactory
from ..models import Comment

pytestmark = pytest.mark.django_db


class TestCommentListView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        comment = CommentFactory(
            community=member.community,
            content="testme",
            content_object=post,
            owner=post.owner,
        )
        response = client.get(
            reverse("comments:list"), HTTP_HOST=comment.community.domain,
        )
        assert len(response.context["object_list"]) == 1

    @pytest.mark.django_db(transaction=True)
    def test_get_search(self, client, member):
        post = PostFactory(community=member.community, owner=member.member)
        comment = CommentFactory(
            community=member.community,
            content="testme",
            content_object=post,
            owner=post.owner,
        )
        response = client.get(
            reverse("comments:list"),
            {"q": "testme"},
            HTTP_HOST=comment.community.domain,
        )
        assert len(response.context["object_list"]) == 1

    def test_get_search_if_empty(self, client, member):
        response = client.get(
            reverse("comments:list"),
            {"q": "testme"},
            HTTP_HOST=member.community.domain,
        )
        assert len(response.context["object_list"]) == 0


class TestCommentDetailView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member, community=member.community, content_object=post,
        )
        notification = NotificationFactory(
            recipient=member.member, content_object=comment, is_read=False
        )
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.community.domain,
        )
        assert response.status_code == 200
        notification.refresh_from_db()
        assert notification.is_read

    def test_get_if_no_content_object(self, client, member):
        comment = CommentFactory(
            owner=member.member, community=member.community, content_object=None,
        )
        response = client.get(
            reverse("comments:detail", args=[comment.id]),
            HTTP_HOST=comment.community.domain,
        )
        assert response.status_code == 200


class TestCommentUpdateView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member, content_object=post, community=member.community,
        )
        response = client.get(reverse("comments:update", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member, content_object=post, community=member.community,
        )
        response = client.post(
            reverse("comments:update", args=[comment.id]), {"content": "new content"},
        )
        assert response.url == post.get_absolute_url()
        comment.refresh_from_db()
        assert comment.content == "new content"
        assert comment.editor == member.member
        assert comment.edited


class TestCommentDeleteView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            owner=member.member, content_object=post, community=member.community,
        )
        response = client.post(reverse("comments:delete", args=[comment.id]))
        assert response.url == post.get_absolute_url()
        assert Comment.objects.count() == 0

    def test_post_by_moderator(self, client, moderator, mailoutbox, send_webpush_mock):
        member = MembershipFactory(community=moderator.community)
        post = PostFactory(community=moderator.community, owner=member.member)
        comment = CommentFactory(
            owner=member.member, content_object=post, community=moderator.community,
        )
        response = client.post(reverse("comments:delete", args=[comment.id]))

        assert response.url == post.get_absolute_url()
        assert Comment.objects.deleted().count() == 1

        assert send_webpush_mock.is_called
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [comment.owner.email]


class TestCommentLikeView:
    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("comments:like", args=[comment.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 204
        like = Like.objects.get()
        assert like.user == member.member


class TestCommentDislikeView:
    def test_post(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        LikeFactory(
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
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("comments:flag", args=[comment.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(community=member.community)
        comment = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        moderator = MembershipFactory(
            community=post.community,
            role=Membership.ROLES.moderator,
            member=UserFactory(),
        )
        response = client.post(
            reverse("comments:flag", args=[comment.id]), data={"reason": "spam"},
        )
        assert response.url == post.get_absolute_url()

        flag = Flag.objects.get()
        assert flag.user == member.member

        notification = Notification.objects.get(recipient=moderator.member)
        assert notification.verb == "flag"


class TestCommentReplyView:
    def test_get(self, client, member):
        post = PostFactory(community=member.community)
        parent = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.get(reverse("comments:reply", args=[parent.id]))
        assert response.status_code == 200

    def test_post(self, client, member, send_webpush_mock):
        post = PostFactory(community=member.community)
        parent = CommentFactory(
            content_object=post,
            community=member.community,
            owner=MembershipFactory(community=member.community).member,
        )
        response = client.post(
            reverse("comments:reply", args=[parent.id]), {"content": "test"}
        )
        assert response.url == parent.content_object.get_absolute_url()
        comment = Comment.objects.get(parent=parent)
        assert comment.owner == member.member
        assert comment.content_object == parent.content_object
        assert comment.parent == parent
