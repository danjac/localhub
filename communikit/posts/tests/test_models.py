# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import factory
import pytest

from django.db.models import signals

from communikit.comments.models import Comment
from communikit.comments.tests.factories import CommentFactory
from communikit.communities.models import Community, Membership
from communikit.posts.models import Post
from communikit.posts.tests.factories import PostFactory
from communikit.users.tests.factories import UserFactory

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

    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, community: Community):
        # owner should not receive any notifications from their own posts
        owner = UserFactory(username="owner")
        moderator = UserFactory()
        mentioned = UserFactory(username="danjac")

        Membership.objects.create(
            member=owner, community=community, role=Membership.ROLES.moderator
        )
        Membership.objects.create(
            member=moderator,
            community=community,
            role=Membership.ROLES.moderator,
        )
        Membership.objects.create(
            member=mentioned, community=community, role=Membership.ROLES.member
        )

        post = PostFactory(
            owner=owner,
            community=community,
            description="hello @danjac from @owner",
        )
        notifications = post.notify(created=True)

        assert notifications[0].recipient == mentioned
        assert notifications[0].verb == "mentioned"

        assert notifications[1].recipient == moderator
        assert notifications[1].verb == "created"

        # ensure saved to db
        assert post.notifications.count() == 2

        # change the description and remove the mention
        post.description = "hello!"
        post.save()

        notifications = post.notify(created=False)

        assert notifications[0].recipient == moderator
        assert notifications[0].verb == "updated"

        assert post.notifications.count() == 3
