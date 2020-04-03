# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


import factory
import pytest
from django.db.models import signals

pytestmark = pytest.mark.django_db


class TestLikeModel:
    @factory.django.mute_signals(signals.post_save)
    def test_notify(self, like, send_webpush_mock):
        notifications = like.notify()
        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.actor == like.user
        assert notification.recipient == like.recipient
        assert notification.content_object == like.content_object
        assert notification.verb == "like"
