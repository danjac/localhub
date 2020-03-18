# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

import pytest
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from taggit.models import Tag

from localhub.comments.factories import CommentFactory
from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Community
from localhub.events.factories import EventFactory
from localhub.events.models import Event
from localhub.flags.models import Flag
from localhub.likes.factories import LikeFactory
from localhub.photos.factories import PhotoFactory
from localhub.photos.models import Photo
from localhub.polls.models import Poll
from localhub.posts.factories import PostFactory
from localhub.posts.models import Post
from localhub.users.factories import UserFactory

from ..models import (
    get_activity_model,
    get_activity_models,
    get_activity_models_dict,
    get_activity_queryset_count,
    get_activity_querysets,
    load_objects,
)

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_with_object_type(self, post, photo, event):

        posts = Post.objects.with_object_type()
        assert posts[0].object_type == "post"

        photos = Photo.objects.with_object_type()
        assert photos[0].object_type == "photo"

        events = Event.objects.with_object_type()
        assert events[0].object_type == "event"

    def test_published_if_false(self):
        PostFactory(published=None)
        assert Post.objects.published().count() == 0

    def test_published_if_true(self):
        PostFactory()
        assert Post.objects.published().count() == 1

    def test_deleted_if_false(self):
        PostFactory(deleted=None)
        assert Post.objects.deleted().count() == 0

    def test_deleted_if_true(self):
        PostFactory(deleted=timezone.now())
        assert Post.objects.deleted().count() == 1

    def test_published_if_deleted(self):
        PostFactory(deleted=timezone.now())
        assert Post.objects.published().count() == 0

    def test_published_or_owner_if_false_and_owner(self, user):
        PostFactory(published=None, owner=user)
        assert Post.objects.published_or_owner(user).count() == 1

    def test_published_or_owner_if_false_and_not_owner(self, user):
        PostFactory(published=None)
        assert Post.objects.published_or_owner(user).count() == 0

    def test_published_or_owner_if_true_and_owner(self, user):
        PostFactory(owner=user)
        assert Post.objects.published_or_owner(user).count() == 1

    def test_published_or_owner_if_deleted(self, user):
        PostFactory(owner=user, deleted=timezone.now())
        assert Post.objects.published_or_owner(user).count() == 1

    def test_published_or_owner_if_true_and_not_owner(self, user):
        PostFactory()
        assert Post.objects.published_or_owner(user).count() == 1

    def test_drafts_if_published_and_owner(self, user):
        PostFactory(owner=user)
        assert Post.objects.drafts(user).count() == 0

    def test_drafts_if_not_published_and_owner(self, user):
        PostFactory(published=None, owner=user)
        assert Post.objects.drafts(user).count() == 1

    def test_drafts_if_published_and_not_owner(self, user):
        PostFactory()
        assert Post.objects.drafts(user).count() == 0

    def test_drafts_if_not_published_and_not_owner(self, user):
        PostFactory(published=None)
        assert Post.objects.drafts(user).count() == 0

    def test_num_reshares(self, post):

        for _ in range(3):
            member = MembershipFactory(community=post.community)
            post.reshare(member.member)

        # non-member

        post.reshare(UserFactory())

        post = (
            Post.objects.with_num_reshares(UserFactory(), post.community)
            .filter(is_reshare=False)
            .first()
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
            Post.objects.with_has_reshared(other).filter(has_reshared=True).count() == 0
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

    def test_with_activity_stream_filters_if_none_set(self, user):

        PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")

        PostFactory()

        assert Post.objects.with_activity_stream_filters(user).count() == 4
        assert Post.objects.with_activity_stream_filters(AnonymousUser()).count() == 4

    def test_with_activity_stream_filters_if_following_users_only(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")

        PostFactory()

        user.activity_stream_filters = ["users"]

        posts = Post.objects.with_activity_stream_filters(user)

        assert len(posts) == 2
        assert my_post in posts
        assert first_post in posts

        assert Post.objects.with_activity_stream_filters(AnonymousUser()).count() == 4

    def test_with_activity_stream_filters_if_following_tags_only(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        PostFactory()

        user.activity_stream_filters = ["tags"]

        posts = Post.objects.with_activity_stream_filters(user)
        assert len(posts) == 2
        assert my_post in posts
        assert second_post in posts

        assert Post.objects.with_activity_stream_filters(AnonymousUser()).count() == 4

    def test_with_activity_stream_filters_if_following_users_and_tags(self, user):

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        PostFactory()

        user.activity_stream_filters = ["tags", "users"]

        posts = Post.objects.with_activity_stream_filters(user).all()
        assert len(posts) == 2

        assert first_post in posts
        assert second_post in posts

    def test_exclude_blocked_users(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        second_post = PostFactory()
        user.blocked.add(first_post.owner)

        posts = Post.objects.exclude_blocked_users(user).all()
        assert len(posts) == 2
        assert my_post in posts
        assert second_post in posts

    def test_exclude_blocked_tags(self, user):
        first_post = PostFactory()
        second_post = PostFactory()
        third_post = PostFactory()

        my_post = PostFactory(owner=user)

        first_post.tags.add("movies")
        second_post.tags.add("movies", "reviews")
        third_post.tags.add("reviews")

        user.blocked_tags.add(Tag.objects.get(name="movies"))
        posts = Post.objects.exclude_blocked_tags(user)

        assert posts.count() == 2
        assert my_post in posts
        assert third_post in posts

    def test_exclude_blocked(self, user):
        first_post = PostFactory()
        second_post = PostFactory()
        third_post = PostFactory()
        fourth_post = PostFactory()

        first_post.tags.add("movies")
        second_post.tags.add("movies", "reviews")
        third_post.tags.add("reviews")

        user.blocked.add(fourth_post.owner)
        user.blocked_tags.add(Tag.objects.get(name="movies"))

        assert Post.objects.exclude_blocked(user).distinct().get() == third_post

    def test_for_community(self, community: Community):

        post = PostFactory(
            community=community, owner=MembershipFactory(community=community).member,
        )
        PostFactory(owner=MembershipFactory(community=community).member)
        PostFactory(owner=MembershipFactory(community=community, active=False).member)
        PostFactory(
            owner=MembershipFactory(community=CommunityFactory(), active=True).member
        )
        PostFactory(community=community)
        PostFactory()

        qs = Post.objects.for_community(community)
        assert qs.count() == 1
        assert qs.first() == post

    def test_with_num_comments(self):
        post = PostFactory()
        member = MembershipFactory(community=post.community)
        CommentFactory.create_batch(
            2, content_object=post, owner=member.member, community=member.community,
        )

        assert Post.objects.with_num_comments(post.community).get().num_comments == 2

    def test_with_num_likes(self, post):
        for _ in range(2):
            LikeFactory(
                content_object=post, community=post.community, recipient=post.owner
            )
        assert Post.objects.with_num_likes().get().num_likes == 2

    def test_with_has_flagged_if_user_has_not_flagged(self, post, user):
        Flag.objects.create(user=user, content_object=post, community=post.community)
        activity = Post.objects.with_has_flagged(UserFactory()).get()
        assert not activity.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, post, user):
        Flag.objects.create(user=user, content_object=post, community=post.community)
        activity = Post.objects.with_has_flagged(user).get()
        assert activity.has_flagged

    def test_with_has_liked_if_user_has_not_liked(self, post, user):
        LikeFactory(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(UserFactory()).get()
        assert not activity.has_liked

    def test_with_has_liked_if_user_has_liked(self, post, user):
        LikeFactory(
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
        activity = Post.objects.with_common_annotations(user, post.community).get()

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


class TestGetActivityModels:
    def test_get_activity_models(self):
        models = get_activity_models()
        assert len(models) == 4
        assert Event in models
        assert Poll in models
        assert Photo in models
        assert Post in models

    def test_get_activity_models_dict(self):
        d = get_activity_models_dict()
        assert d == {
            "event": Event,
            "poll": Poll,
            "photo": Photo,
            "post": Post,
        }

    def test_get_activity_model(self):
        assert get_activity_model("post") == Post

    def test_get_activity_model_if_invalid(self):
        with pytest.raises(KeyError):
            get_activity_model("something")


class TestGetActivityQuerysets:
    def test_get_activity_querysets(self):
        post = PostFactory(published=timezone.now() - timedelta(days=1))
        event = EventFactory(published=timezone.now() - timedelta(days=3))
        PhotoFactory(published=None)

        qs, querysets = get_activity_querysets(
            lambda model: model.objects.filter(published__isnull=False),
            ordering="-published",
        )

        assert len(qs) == 2
        assert len(querysets) == 4

        items = load_objects(qs, querysets)
        assert len(items) == 2

        assert items[0]["pk"] == post.id
        assert items[0]["object"] == post
        assert items[0]["object_type"] == "post"

        assert items[1]["pk"] == event.id
        assert items[1]["object"] == event
        assert items[1]["object_type"] == "event"


class TestGetActivityQuerysetCount:
    def test_get_activity_queryset_count(self):
        PostFactory()
        EventFactory()

        assert get_activity_queryset_count(lambda model: model.objects.all()) == 2
