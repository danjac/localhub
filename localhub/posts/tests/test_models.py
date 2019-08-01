# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import factory
import pytest

from django.conf import settings
from django.db.models import signals

from taggit.models import Tag

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Community, Membership
from localhub.communities.tests.factories import MembershipFactory
from localhub.posts.models import Post
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_reshare(self, post: Post, user: settings.AUTH_USER_MODEL):

        reshared = post.reshare(user)
        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user

    def test_reshare_a_reshare(
        self, post: Post, user: settings.AUTH_USER_MODEL
    ):

        reshared = post.reshare(user)
        reshared.reshare(UserFactory())

        assert reshared.title == post.title
        assert reshared.description == post.description
        assert reshared.is_reshare
        assert reshared.parent == post
        assert reshared.community == post.community
        assert reshared.owner == user

    def test_delete_comments_on_delete(self, post: Post):
        CommentFactory(content_object=post)
        post.delete()
        assert Comment.objects.count() == 0

    def test_breadcrumbs(self, post: Post):
        breadcrumbs = post.get_breadcrumbs()
        assert len(breadcrumbs) == 3
        assert breadcrumbs[2][0] == post.get_absolute_url()

    def test_get_domain_if_no_url(self):
        assert Post().get_domain() is None

    def test_get_domain_if_url(self):
        assert Post(url="http://google.com").get_domain() == "google.com"

    def test_get_content_warning_tags_if_any(self):
        post = PostFactory(description="This post is #nsfw!")
        assert post.get_content_warning_tags() == {"nsfw"}

    def test_get_content_warning_tags_if_none(self):
        post = PostFactory(description="This post is #legit")
        assert post.get_content_warning_tags() == set()

    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, community: Community):
        # owner should not receive any notifications from their own posts
        owner = MembershipFactory(
            community=community, role=Membership.ROLES.moderator
        ).member

        moderator = MembershipFactory(
            community=community, role=Membership.ROLES.moderator
        ).member

        mentioned = MembershipFactory(
            member=UserFactory(username="danjac"),
            community=community,
            role=Membership.ROLES.member,
        ).member

        # ensure we just have one notification for multiple tags

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        tag_follower = MembershipFactory(community=community).member
        tag_follower.following_tags.add(movies, reviews)

        # owner should also follow tags to ensure they aren't notified
        owner.following_tags.add(movies, reviews)

        assert tag_follower.following_tags.count() == 2

        user_follower = MembershipFactory(community=community).member
        user_follower.following.add(post.owner)

        notifications = post.notify(created=True)
        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == post.owner
        assert notifications[1].verb == "tag"

        assert notifications[2].recipient == user_follower
        assert notifications[2].actor == post.owner
        assert notifications[2].verb == "following"

        assert notifications[3].recipient == moderator
        assert notifications[3].actor == post.owner
        assert notifications[3].verb == "review"

        # edit by moderator
        post.editor = moderator
        post.save()

        notifications = post.notify(created=False)
        assert len(notifications) == 1

        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == moderator
        assert notifications[0].verb == "edit"

        # reshare
        reshare = post.reshare(UserFactory())
        notifications = reshare.notify(created=True)
        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == reshare.owner
        assert notifications[0].verb == "mention"

        assert notifications[1].recipient == tag_follower
        assert notifications[1].actor == reshare.owner
        assert notifications[1].verb == "tag"

        assert notifications[2].recipient == post.owner
        assert notifications[2].actor == reshare.owner
        assert notifications[2].verb == "reshare"

        assert notifications[3].recipient == moderator
        assert notifications[3].actor == reshare.owner
        assert notifications[3].verb == "review"
