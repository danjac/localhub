# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from taggit.models import Tag

from localhub.communities.models import Community
from localhub.communities.tests.factories import (
    CommunityFactory,
    MembershipFactory,
)
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.posts.models import Post
from localhub.comments.tests.factories import CommentFactory
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_num_reshares(self, post):

        for _ in range(3):
            post.reshare(UserFactory())

        post = (
            Post.objects.with_num_reshares().filter(is_reshare=False).first()
        )
        assert post.num_reshares == 3

    def test_has_reshared(self, post, user):

        first = PostFactory()
        PostFactory()

        other = UserFactory()

        first.reshare(user)

        posts = Post.objects.with_has_reshared(user).filter(has_reshared=True)
        assert len(posts) == 1
        assert posts[0] == first

        assert (
            Post.objects.with_has_reshared(other)
            .filter(has_reshared=True)
            .count()
            == 0
        )
        assert (
            Post.objects.with_has_reshared(AnonymousUser())
            .filter(has_reshared=True)
            .count()
            == 0
        )

    def test_following_users(self, user):
        first_post = PostFactory()
        PostFactory()
        user.following.add(first_post.owner)
        assert Post.objects.following_users(user).get() == first_post
        assert Post.objects.following_users(AnonymousUser()).count() == 2

    def test_following_tags(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        first_post.tags.add("movies")

        second_post = PostFactory()
        second_post.tags.add("reviews")

        user.following_tags.add(Tag.objects.get(name="movies"))

        posts = Post.objects.following_tags(user).all()

        assert len(posts) == 2

        assert my_post in posts
        assert first_post in posts

        assert Post.objects.following_tags(AnonymousUser()).count() == 3

    def test_following_if_no_preferences(self, user):

        PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")

        PostFactory()

        assert Post.objects.following(user).count() == 4
        assert Post.objects.following(AnonymousUser()).count() == 4

    def test_following_users_only(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")

        PostFactory()

        user.home_page_filters = ["users"]

        posts = Post.objects.following(user)

        assert len(posts) == 2
        assert my_post in posts
        assert first_post in posts

        assert Post.objects.following(AnonymousUser()).count() == 4

    def test_following_tags_only(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        PostFactory()

        user.home_page_filters = ["tags"]

        posts = Post.objects.following(user)
        assert len(posts) == 2
        assert my_post in posts
        assert second_post in posts

        assert Post.objects.following(AnonymousUser()).count() == 4

    def test_following_users_and_tags(self, user):

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        PostFactory()

        user.home_page_filters = ["tags", "users"]

        posts = Post.objects.following(user).all()
        assert len(posts) == 2

        assert first_post in posts
        assert second_post in posts

    def test_blocked_users(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        second_post = PostFactory()
        user.blocked.add(first_post.owner)

        posts = Post.objects.blocked_users(user).all()
        assert len(posts) == 2
        assert my_post in posts
        assert second_post in posts

    def test_blocked_tags(self, user):
        first_post = PostFactory()
        second_post = PostFactory()
        third_post = PostFactory()

        my_post = PostFactory(owner=user)

        first_post.tags.add("movies")
        second_post.tags.add("movies", "reviews")
        third_post.tags.add("reviews")

        user.blocked_tags.add(Tag.objects.get(name="movies"))
        posts = Post.objects.blocked_tags(user)

        assert posts.count() == 2
        assert my_post in posts
        assert third_post in posts

    def test_blocked(self, user):
        first_post = PostFactory()
        second_post = PostFactory()
        third_post = PostFactory()
        fourth_post = PostFactory()

        first_post.tags.add("movies")
        second_post.tags.add("movies", "reviews")
        third_post.tags.add("reviews")

        user.blocked.add(fourth_post.owner)
        user.blocked_tags.add(Tag.objects.get(name="movies"))

        assert Post.objects.blocked(user).distinct().get() == third_post

    def test_for_community(self, community: Community):

        post = PostFactory(
            community=community,
            owner=MembershipFactory(community=community).member,
        )
        PostFactory(owner=MembershipFactory(community=community).member)
        PostFactory(
            owner=MembershipFactory(community=community, active=False).member
        )
        PostFactory(
            owner=MembershipFactory(
                community=CommunityFactory(), active=True
            ).member
        )
        PostFactory(community=community)
        PostFactory()

        qs = Post.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == post

    def test_with_num_comments(self):
        post = PostFactory()
        CommentFactory.create_batch(2, content_object=post)
        assert Post.objects.with_num_comments().get().num_comments == 2

    def test_with_num_likes(self, post):
        for _ in range(2):
            Like.objects.create(
                user=UserFactory(),
                content_object=post,
                community=post.community,
                recipient=post.owner,
            )

        assert Post.objects.with_num_likes().get().num_likes == 2

    def test_with_has_flagged_if_user_has_not_flagged(self, post, user):
        Flag.objects.create(
            user=user, content_object=post, community=post.community
        )
        activity = Post.objects.with_has_flagged(UserFactory()).get()
        assert not activity.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, post, user):
        Flag.objects.create(
            user=user, content_object=post, community=post.community
        )
        activity = Post.objects.with_has_flagged(user).get()
        assert activity.has_flagged

    def test_with_has_liked_if_user_has_not_liked(self, post, user):
        Like.objects.create(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(UserFactory()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_liked(self, post, user):
        Like.objects.create(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(user).get()
        assert activity.has_liked

    def test_with_common_annotations_if_anonymous(self, post):
        activity = Post.objects.with_common_annotations(
            AnonymousUser(), post.community
        ).get()

        assert hasattr(activity, "num_comments")
        assert not hasattr(activity, "num_likes")
        assert not hasattr(activity, "is_flagged")
        assert not hasattr(activity, "has_liked")
        assert not hasattr(activity, "has_flagged")

    def test_with_common_annotations_if_authenticated(self, post, user):
        activity = Post.objects.with_common_annotations(
            user, post.community
        ).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert not hasattr(activity, "is_flagged")

    def test_with_common_annotations_if_moderator(self, moderator):
        PostFactory(community=moderator.community)
        activity = Post.objects.with_common_annotations(
            moderator.member, moderator.community
        ).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert hasattr(activity, "is_flagged")

    def test_search(self):
        post = PostFactory(title="random thing")
        # normally fired when transaction commits
        post.search_indexer.update()
        result = Post.objects.search("random thing").get()
        assert result.rank
