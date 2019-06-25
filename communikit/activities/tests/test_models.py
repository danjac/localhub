# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.activities.models import Activity, Like
from communikit.comments.models import Comment
from communikit.communities.models import Membership
from communikit.flags.models import Flag
from communikit.posts.models import Post
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_with_num_comments(self, comment: Comment):
        activity = Activity.objects.with_num_comments().get()
        assert activity.num_comments == 1

    def test_with_num_likes(self, post: Post, user: settings.AUTH_USER_MODEL):
        Like.objects.create(user=user, activity=post)

        activity = Activity.objects.with_num_likes().get()
        assert activity.num_likes == 1

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
        Like.objects.create(user=user, activity=post)
        activity = Activity.objects.with_has_liked(UserFactory()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_liked(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):
        Like.objects.create(user=user, activity=post)
        activity = Activity.objects.with_has_liked(user).get()
        assert activity.has_liked

    def test_with_common_annotations_if_anonymous(self, post: Post):
        activity = Activity.objects.with_common_annotations(
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
        activity = Activity.objects.with_common_annotations(
            post.community, user
        ).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert not hasattr(activity, "is_flagged")

    def test_with_common_annotations_if_moderator(self, moderator: Membership):
        PostFactory(community=moderator.community)
        activity = Activity.objects.with_common_annotations(
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
        result = Activity.objects.search("random thing").get()
        assert result.rank
