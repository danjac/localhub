# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import factory
import pytest

from django.db.models import signals

from taggit.models import Tag

from localhub.comments.models import Comment
from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Community, Membership
from localhub.posts.models import Post
from localhub.posts.tests.factories import PostFactory
from localhub.subscriptions.models import Subscription
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
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
        owner = UserFactory(username="owner")
        moderator = UserFactory()

        Membership.objects.create(
            member=owner, community=community, role=Membership.ROLES.moderator
        )

        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )
        mentioned = UserFactory(username="danjac")

        Membership.objects.create(
            member=mentioned, community=community, role=Membership.ROLES.member
        )

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner #movies #reviews",
        )

        movies = Tag.objects.create(name="movies")
        reviews = Tag.objects.create(name="reviews")

        tag_subscriber = UserFactory()

        # ensure we just have one notification for multiple tags

        Subscription.objects.create(
            subscriber=tag_subscriber,
            content_object=movies,
            community=post.community,
        )

        Subscription.objects.create(
            subscriber=tag_subscriber,
            content_object=reviews,
            community=post.community,
        )

        user_subscriber = UserFactory()

        Subscription.objects.create(
            subscriber=user_subscriber,
            content_object=post.owner,
            community=post.community,
        )

        notifications = post.notify(created=True)
        assert len(notifications) == 4

        assert notifications[0].recipient == mentioned
        assert notifications[0].actor == post.owner
        assert notifications[0].verb == "mentioned"

        assert notifications[1].recipient == tag_subscriber
        assert notifications[1].actor == post.owner
        assert notifications[1].verb == "tagged"

        assert notifications[2].recipient == user_subscriber
        assert notifications[2].actor == post.owner
        assert notifications[2].verb == "created"

        assert notifications[3].recipient == moderator
        assert notifications[3].actor == post.owner
        assert notifications[3].verb == "created"

        # edit by moderator
        post.editor = moderator
        post.save()

        notifications = post.notify(created=False)
        assert len(notifications) == 1

        assert notifications[0].recipient == post.owner
        assert notifications[0].actor == moderator
        assert notifications[0].verb == "moderated"
