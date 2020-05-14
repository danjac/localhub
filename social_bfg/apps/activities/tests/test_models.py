# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.utils import timezone

# Third Party Libraries
import pytest
from taggit.models import Tag

# Social-BFG
from social_bfg.apps.bookmarks.factories import BookmarkFactory
from social_bfg.apps.comments.factories import CommentFactory
from social_bfg.apps.communities.factories import CommunityFactory, MembershipFactory
from social_bfg.apps.communities.models import Community
from social_bfg.apps.events.models import Event
from social_bfg.apps.flags.factories import FlagFactory
from social_bfg.apps.likes.factories import LikeFactory
from social_bfg.apps.notifications.factories import NotificationFactory
from social_bfg.apps.photos.models import Photo
from social_bfg.apps.posts.factories import PostFactory
from social_bfg.apps.posts.models import Post
from social_bfg.apps.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestActivityManager:
    def test_search(self, member, transactional_db):
        PostFactory(community=member.community, title="test", owner=member.member)
        results = Post.objects.search("test")
        assert results.count() == 1

    def test_search_negative_result(self, member, transactional_db):
        PostFactory(community=member.community, title="test", owner=member.member)
        results = Post.objects.search("xyz")
        assert results.count() == 0

    def test_search_mentions(self, member, transactional_db):
        PostFactory(
            community=member.community,
            title="test",
            owner=member.member,
            mentions="@danjac @tester",
        )
        results = Post.objects.search("@danjac")
        assert results.count() == 1

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

    def test_private_if_published_and_owner(self, user):
        PostFactory(owner=user)
        assert Post.objects.private(user).count() == 0

    def test_private_if_not_published_and_owner(self, user):
        PostFactory(published=None, owner=user)
        assert Post.objects.private(user).count() == 1

    def test_private_if_published_and_not_owner(self, user):
        PostFactory()
        assert Post.objects.private(user).count() == 0

    def test_private_if_not_published_and_not_owner(self, user):
        PostFactory(published=None)
        assert Post.objects.private(user).count() == 0

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

    def test_unreshared(self, post, user, anonymous_user):

        first = PostFactory()
        PostFactory()

        other = UserFactory()

        first.reshare(user)

        assert Post.objects.unreshared(other).count() == 4
        assert Post.objects.unreshared(anonymous_user).count() == 4

        posts = Post.objects.unreshared(user)
        # incl. reshared post
        assert posts.count() == 3
        assert first not in posts

    def test_has_reshared(self, post, user, anonymous_user):

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
            Post.objects.with_has_reshared(anonymous_user)
            .filter(has_reshared=True)
            .count()
            == 0
        )

    def test_following_users(self, user, anonymous_user):
        first_post = PostFactory()
        PostFactory()
        user.following.add(first_post.owner)
        assert Post.objects.following_users(user).get() == first_post
        assert Post.objects.following_users(anonymous_user).count() == 2

    def test_following_tags(self, user, anonymous_user):

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

        assert Post.objects.following_tags(anonymous_user).count() == 3

    def test_with_activity_stream_filters_if_none_set(self, user, anonymous_user):

        PostFactory(owner=user)

        first_post = PostFactory()
        user.following.add(first_post.owner)

        second_post = PostFactory()
        second_post.tags.add("reviews")

        PostFactory()

        assert Post.objects.with_activity_stream_filters(user).count() == 4
        assert Post.objects.with_activity_stream_filters(anonymous_user).count() == 4

    def test_with_activity_stream_filters_if_following_users_only(
        self, user, anonymous_user
    ):

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

        assert Post.objects.with_activity_stream_filters(anonymous_user).count() == 4

    def test_with_activity_stream_filters_if_following_tags_only(
        self, user, anonymous_user
    ):

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

        assert Post.objects.with_activity_stream_filters(anonymous_user).count() == 4

    def test_with_activity_stream_filters_if_following_users_and_tags_mutually_exclusive(
        self, user
    ):

        # following user, but not tag
        first_post = PostFactory()
        user.following.add(first_post.owner)

        # following tag, but not user
        second_post = PostFactory()
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        PostFactory()

        user.activity_stream_filters = ["tags", "users"]

        posts = Post.objects.with_activity_stream_filters(user).all()
        assert len(posts) == 2
        assert first_post in posts
        assert second_post in posts

    def test_with_activity_stream_filters_if_following_users_and_tags_with_results(
        self, user
    ):

        # following user and tag
        first_post = PostFactory()
        first_post.tags.add("reviews")
        user.following.add(first_post.owner)

        # following tag, but not user
        second_post = PostFactory(owner=first_post.owner)
        second_post.tags.add("reviews")
        user.following_tags.add(Tag.objects.get(name="reviews"))

        # sanity check
        PostFactory()

        user.activity_stream_filters = ["tags", "users"]

        posts = Post.objects.with_activity_stream_filters(user).all()
        assert len(posts) == 2
        assert first_post in posts
        assert second_post in posts

    def test_exclude_blocked_users_if_user_blocking(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        second_post = PostFactory()
        user.blocked.add(first_post.owner)

        posts = Post.objects.exclude_blocked_users(user).all()
        assert len(posts) == 2
        assert my_post in posts
        assert second_post in posts

    def test_exclude_blocked_users_if_user_blocked(self, user):

        my_post = PostFactory(owner=user)

        first_post = PostFactory()
        second_post = PostFactory()
        user.blockers.add(first_post.owner)

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
        FlagFactory(user=user, content_object=post, community=post.community)
        activity = Post.objects.with_has_flagged(UserFactory()).get()
        assert not activity.has_flagged

    def test_with_has_flagged_if_user_has_flagged(self, post, user):
        FlagFactory(user=user, content_object=post, community=post.community)
        activity = Post.objects.with_has_flagged(user).get()
        assert activity.has_flagged

    def test_with_has_bookmarked_if_user_has_not_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        activity = Post.objects.with_has_bookmarked(UserFactory()).get()
        assert not activity.has_bookmarked

    def test_with_has_bookmarked_if_user_has_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        activity = Post.objects.with_has_bookmarked(user).get()
        assert activity.has_bookmarked

    def test_bookmarked_if_anon_user(self, post, anonymous_user):
        BookmarkFactory(
            content_object=post, community=post.community,
        )
        assert Post.objects.bookmarked(anonymous_user).count() == 0

    def test_bookmarked_if_user_has_not_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        assert Post.objects.bookmarked(UserFactory()).count() == 0

    def test_bookmarked_if_user_has_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        posts = Post.objects.bookmarked(user)
        assert posts.count() == 1
        assert posts.first().has_bookmarked

    def test_with_bookmarked_timestamp_if_user_has_not_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        # test with *another* user
        post = Post.objects.with_bookmarked_timestamp(UserFactory()).first()
        assert post.bookmarked is None

    def test_with_bookmarked_timestamp_if_user_has_bookmarked(self, post, user):
        BookmarkFactory(
            user=user, content_object=post, community=post.community,
        )
        post = Post.objects.with_bookmarked_timestamp(user).first()
        assert post.bookmarked is not None

    def test_with_has_liked_if_anon_user(self, post, anonymous_user):
        LikeFactory(
            content_object=post, community=post.community, recipient=post.owner,
        )
        activity = Post.objects.with_has_liked(anonymous_user).get()
        assert not activity.has_liked

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

    def test_liked_if_user_has_not_liked(self, post, user):
        LikeFactory(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        assert Post.objects.liked(UserFactory()).count() == 0

    def test_liked_if_user_has_liked(self, post, user):
        LikeFactory(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        posts = Post.objects.liked(user)
        assert posts.count() == 1
        assert posts.first().has_liked

    def test_with_liked_timestamp_if_user_has_liked(self, post, user):
        LikeFactory(
            user=user,
            content_object=post,
            community=post.community,
            recipient=post.owner,
        )
        post = Post.objects.with_liked_timestamp(user).first()
        assert post.liked is not None

    def test_with_liked_timestamp_if_user_has_not_liked(self, post, user):
        post = Post.objects.with_liked_timestamp(user).first()
        assert post.liked is None

    def test_with_common_annotations_if_anonymous(self, post, anonymous_user):
        activity = Post.objects.with_common_annotations(
            anonymous_user, post.community
        ).get()

        assert hasattr(activity, "num_comments")
        assert not hasattr(activity, "num_likes")
        assert not hasattr(activity, "is_flagged")
        assert not hasattr(activity, "has_liked")
        assert not hasattr(activity, "has_flagged")
        assert not hasattr(activity, "is_new")

    def test_with_common_annotations_if_authenticated(self, post, user):
        activity = Post.objects.with_common_annotations(user, post.community).get()

        assert hasattr(activity, "num_comments")
        assert hasattr(activity, "num_likes")
        assert hasattr(activity, "has_liked")
        assert hasattr(activity, "has_flagged")
        assert hasattr(activity, "is_new")
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
        assert hasattr(activity, "is_new")

    def test_with_is_new_if_notification_is_unread(self, post, member):
        NotificationFactory(
            verb="mention", recipient=member.member, content_object=post, is_read=False
        )

        posts = Post.objects.with_is_new(member.member)
        first = posts.first()
        assert first.is_new

    def test_with_is_new_if_notification_is_unread_anon(
        self, post, member, anonymous_user
    ):
        NotificationFactory(
            verb="mention", recipient=member.member, content_object=post, is_read=False
        )

        posts = Post.objects.with_is_new(anonymous_user)
        first = posts.first()
        assert not first.is_new

    def test_with_is_new_if_notification_is_read(self, post, member):
        NotificationFactory(
            verb="mention", recipient=member.member, content_object=post, is_read=True
        )

        posts = Post.objects.with_is_new(member.member)
        first = posts.first()
        assert not first.is_new

    def test_with_is_new_if_notification_is_unread_wrong_recipient(self, post, member):
        NotificationFactory(verb="mention", content_object=post, is_read=False)

        posts = Post.objects.with_is_new(member.member)
        first = posts.first()
        assert not first.is_new
