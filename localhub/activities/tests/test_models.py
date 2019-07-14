# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Membership
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.posts.models import Post
from localhub.comments.tests.factories import CommentFactory
from localhub.posts.tests.factories import PostFactory
from localhub.subscriptions.models import Subscription
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_following(self, user: settings.AUTH_USER_MODEL):
        not_followed = PostFactory()
        my_post = PostFactory(owner=user)
        followed = PostFactory()
        Subscription.objects.create(
            subscriber=user,
            community=followed.community,
            content_object=followed.owner,
        )

        posts = Post.objects.following(user)
        assert posts.count() == 2
        assert not_followed not in posts
        assert my_post in posts
        assert followed in posts

    def test_with_num_comments(self):
        post = PostFactory()
        CommentFactory.create_batch(2, content_object=post)
        assert Post.objects.with_num_comments().get().num_comments == 2

    def test_with_num_likes(self, post: Post):
        for _ in range(2):
            Like.objects.create(
                user=UserFactory(),
                content_object=post,
                community=post.community,
                recipient=post.owner,
            )

        assert Post.objects.with_num_likes().get().num_likes == 2

    def test_with_has_flagged_if_user_has_not_flagged(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Flag.objects.create(
            user=user, content_object=post, community=post.community
        )
        activity = Post.objects.with_has_flagged(UserFactory()).get()
        assert not activity.has_flagged

    def test_with_has_flagged_if_user_has_flagged(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Flag.objects.create(
            user=user, content_object=post, community=post.community
        )
        activity = Post.objects.with_has_flagged(user).get()
        assert activity.has_flagged

    def test_with_has_liked_if_user_has_not_liked(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(UserFactory()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_liked(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(user).get()
        assert activity.has_liked

    def test_with_common_annotations_if_anonymous(self, post: Post):
        activity = Post.objects.with_common_annotations(
            post.community, AnonymousUser()
        ).get()

        assert hasattr(activity, "num_comments")
        assert not hasattr(activity, "num_likes")
        assert not hasattr(activity, "is_flagged")
        assert not hasattr(activity, "has_liked")
        assert not hasattr(activity, "has_flagged")

    def test_with_common_annotations_if_authenticated(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        activity = Post.objects.with_common_annotations(
            post.community, user
        ).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert not hasattr(activity, "is_flagged")

    def test_with_common_annotations_if_moderator(self, moderator: Membership):
        PostFactory(community=moderator.community)
        activity = Post.objects.with_common_annotations(
            moderator.community, moderator.member
        ).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert hasattr(activity, "is_flagged")

    def test_search(self):
        post = PostFactory(title="random thing")
        # normally fired when transaction commits
        post.make_search_updater()()
        result = Post.objects.search("random thing").get()
        assert result.rank
