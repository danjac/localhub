# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import factory
import pytest

from django.db.models import signals
from django.conf import settings

from localhub.comments.tests.factories import CommentFactory
from localhub.communities.models import Membership
from localhub.flags.models import Flag
from localhub.posts.tests.factories import PostFactory


pytestmark = pytest.mark.django_db


class TestFlagModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify_comment(
        self, user: settings.AUTH_USER_MODEL, moderator: Membership
    ):
        post = PostFactory(community=moderator.community)
        comment = CommentFactory(content_object=post)
        flag = Flag.objects.create(
            content_object=comment, user=user, community=post.community
        )
        notifications = flag.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == user
        assert notification.recipient == moderator.member
        assert notification.content_object == comment
        assert notification.verb == "flagged"

    @factory.django.mute_signals(signals.post_save)
    def test_notify_post(
        self, user: settings.AUTH_USER_MODEL, moderator: Membership
    ):
        post = PostFactory(community=moderator.community)
        flag = Flag.objects.create(
            content_object=post, user=user, community=post.community
        )
        notifications = flag.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == user
        assert notification.recipient == moderator.member
        assert notification.content_object == post
        assert notification.verb == "flagged"
