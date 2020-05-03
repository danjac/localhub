# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.db.models import signals

import factory
import pytest

from social_bfg.apps.comments.factories import CommentFactory
from social_bfg.apps.posts.factories import PostFactory

from ..factories import FlagFactory

pytestmark = pytest.mark.django_db


class TestFlagModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify_comment(self, user, moderator, send_webpush_mock):

        moderator.member.notification_preferences = ["flag"]
        moderator.member.save()

        post = PostFactory(community=moderator.community)
        comment = CommentFactory(content_object=post)
        flag = FlagFactory(content_object=comment, user=user, community=post.community)
        notifications = flag.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == user
        assert notification.recipient == moderator.member
        assert notification.content_object == comment
        assert notification.verb == "flag"

    @factory.django.mute_signals(signals.post_save)
    def test_notify_post(self, user, moderator, send_webpush_mock):
        moderator.member.notification_preferences = ["flag"]
        moderator.member.save()

        post = PostFactory(community=moderator.community)
        flag = FlagFactory(content_object=post, user=user, community=post.community)
        notifications = flag.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == user
        assert notification.recipient == moderator.member
        assert notification.content_object == post
        assert notification.verb == "flag"
