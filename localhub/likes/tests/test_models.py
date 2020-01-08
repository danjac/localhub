# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import factory
import pytest
from django.db.models import signals

from ..models import Like

pytestmark = pytest.mark.django_db


class TestLikeModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, user, post):
        post.owner.notification_preferences = ["like"]
        post.owner.save()
        like = Like.objects.create(
            content_object=post,
            user=user,
            community=post.community,
            recipient=post.owner,
        )
        notifications = like.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == user
        assert notification.recipient == post.owner
        assert notification.content_object == post
        assert notification.verb == "like"
