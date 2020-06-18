# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest
from taggit.models import Tag

# Localhub
# Social-BFG
from localhub.apps.comments.factories import CommentFactory
from localhub.apps.comments.models import Comment
from localhub.apps.communities.factories import CommunityFactory, MembershipFactory
from localhub.apps.communities.models import Membership
from localhub.apps.flags.factories import FlagFactory
from localhub.apps.likes.factories import LikeFactory
from localhub.apps.notifications.factories import NotificationFactory
from localhub.apps.users.factories import UserFactory

# Local
from ..factories import PostFactory
from ..models import Post

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_mentions_changed(self, post):

        post = Post.objects.get(pk=post.id)
        assert not post.mentions_changed()
        post.mentions = "@tester"
        assert post.mentions_changed()
        post.reset_tracker()
        assert not post.mentions_changed()

    def test_hashtags_changed(self, post):

        post = Post.objects.get(pk=post.id)
        assert not post.hashtags_changed()
        post.hashtags = "#rust"
        assert post.hashtags_changed()
        post.reset_tracker()
        assert not post.hashtags_changed()

    def test_get_absolute_url(self):
        """
        If non-ASCII slug append to url
        """
        post = PostFactory(title="test post")
        assert post.get_absolute_url() == f"/posts/{post.id}/test-post/"

    def test_get_absolute_url_if_non_ascii(self):
        """
        If non-ASCII slug is empty just use ID
        """
        post = PostFactory(title="中国研究方法")
        assert post.get_absolute_url() == f"/posts/{post.id}/zhong-guo-yan-jiu-fang-fa/"

    def test_extract_mentions(self):
        post = Post(
            description="hello @danjac",
            mentions="@weegill @testuser",
            title="this is for @someone",
        )
        assert post.extract_mentions() == {"danjac", "weegill", "testuser", "someone"}

    def test_extract_hashtags(self):

        post = Post(
            title="something #movies",
            description="content #movies and #films",
            hashtags="#netflix",
        )
        assert post.extract_hashtags() == {"movies", "films", "netflix"}

    def test_save_tags(self, post):

        post.description = "a post about #movies"
        post.save()

        tags = [t.name for t in post.tags.all()]
        assert "movies" in tags

        # clear tags
        post.description = "a post about movies"
        post.save()
        assert post.tags.count() == 0

    def test_reshare(self, post, user):

        reshared = post.reshare(user)
        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user
        assert reshared.published

    def test_update_reshares(self, post, user):

        reshared = post.reshare(user)
        post.title = "a new title"
        post.save()
        post.update_reshares()
        reshared.refresh_from_db()
        assert reshared.title == "a new title"

    def test_reshare_a_reshare(self, post, user):

        reshared = post.reshare(user)
        reshared.reshare(UserFactory())

        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user
        assert reshared.published

    def test_manage_comments_on_delete(self, post):
        # comment relations should be set to NULL.
        CommentFactory(content_object=post)
        post.delete()
        assert Comment.objects.count() == 1
        comment = Comment.objects.first()
        assert comment.object_id is None
        assert comment.content_type is None
        assert comment.content_object is None

    def test_get_domain_if_no_url(self):
        assert Post().get_domain() == ""

    def test_get_domain_if_url(self):
        assert Post(url="http://google.com").get_domain() == "google.com"

    def test_get_content_warning_tags_if_any(self):
        post = PostFactory(description="This post is #nsfw!")
        assert post.get_content_warning_tags() == {"nsfw"}

    def test_get_content_warning_tags_if_none(self):
        post = PostFactory(description="This post is #legit")
        assert post.get_content_warning_tags() == set()

    def test_notify_on_publish(self, community, send_webpush_mock):
        # owner should not receive any notifications from their own posts
        owner = MembershipFactory(
            community=community, role=Membership.Role.MODERATOR
        ).member

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.Role.MEMBER,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        tag_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        tag_follower.following_tags.add(movies, reviews)

        # owner should also follow tags to ensure they aren't notified
        owner.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        user_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        user_follower.following.add(post.owner)

        notifications = post.notify_on_publish()
        assert len(notifications) == 3

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == post.owner
        assert notifications[1].verb == "followed_tag"

        assert notifications[2].recipient == user_follower
        assert notifications[2].actor == post.owner
        assert notifications[2].verb == "followed_user"

    def test_notify_on_delete(self, post, moderator, send_webpush_mock):
        notifications = post.notify_on_delete(moderator.member)

        assert len(notifications) == 1
        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == moderator.member
        assert notifications[0].verb == "delete"

    def test_notify_on_update_moderator_edit(self, community, send_webpush_mock):

        owner = MembershipFactory(community=community).member

        member = MembershipFactory(
            community=community, member=UserFactory(username="danjac"),
        ).member

        moderator = MembershipFactory(community=community,).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello from @owner #movies #reviews",
        )

        post.description = "hello @danjac"
        post.editor = moderator
        post.save()

        notifications = post.notify_on_update()
        assert len(notifications) == 2

        assert notifications[0].recipient == member
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == post.owner
        assert notifications[1].actor == moderator
        assert notifications[1].verb == "edit"

    def test_notify_on_update(self, community, send_webpush_mock):

        owner = MembershipFactory(community=community).member

        member = MembershipFactory(
            community=community, member=UserFactory(username="danjac"),
        ).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello from @owner #movies #reviews",
        )

        post.description = "hello @danjac"
        post.save()

        notifications = post.notify_on_update()
        assert len(notifications) == 1

        assert notifications[0].recipient == member
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

    def test_notify_on_publish_reshare(self, community, send_webpush_mock):

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.Role.MEMBER,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        tag_follower = MembershipFactory(
            community=community, member=UserFactory(),
        ).member
        tag_follower.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        owner = MembershipFactory(community=community,).member

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        # reshare
        reshare = post.reshare(UserFactory())
        notifications = list(reshare.notify_on_publish())
        assert len(notifications) == 3

        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == reshare.owner
        assert notifications[0].verb == "reshare"

        assert notifications[1].recipient == mentioned
        assert notifications[1].actor == reshare.owner
        assert notifications[1].verb == "mention"

        assert notifications[2].recipient == tag_follower
        assert notifications[2].actor == reshare.owner
        assert notifications[2].verb == "followed_tag"

    def test_soft_delete(self, post, mocker, send_webpush_mock):
        CommentFactory(content_object=post)
        NotificationFactory(content_object=post)
        FlagFactory(content_object=post)
        LikeFactory(content_object=post)

        mock_soft_delete = mocker.patch("localhub.apps.activities.signals.soft_delete")
        post.soft_delete()
        assert mock_soft_delete.called_with(sender=Post, instance=post)

        post.refresh_from_db()

        assert post.published is None
        assert post.deleted is not None

        # comments should NOT be deleted but refs should be removed

        assert Comment.objects.count() == 1
        assert post.get_comments().count() == 0
        assert post.get_notifications().count() == 0
        assert post.get_likes().count() == 0
        assert post.get_flags().count() == 0

    def test_is_sensitive_anon_user(self, anonymous_user):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert post.is_content_sensitive(anonymous_user)

    def test_is_sensitive_auth_ok(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert not post.is_content_sensitive(UserFactory(show_sensitive_content=True))

    def test_is_sensitive_auth_not_ok(self):

        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert post.is_content_sensitive(UserFactory(show_sensitive_content=False))

    def test_not_is_sensitive_anon_user(self, anonymous_user):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not post.is_content_sensitive(anonymous_user)

    def test_not_is_sensitive_auth(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not post.is_content_sensitive(UserFactory(show_sensitive_content=False))
