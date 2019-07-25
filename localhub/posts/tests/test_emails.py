# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List


from localhub.activities.emails import (
    send_activity_deleted_email,
    send_activity_notification_email,
)
from localhub.posts.models import Post
from localhub.notifications.models import Notification
from localhub.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestSendPostNotificationEmail:
    def test_if_enabled(self, post: Post, mailoutbox: List):
        moderator = UserFactory(email_preferences=["reviews"])

        notification = Notification.objects.create(
            content_object=post,
            community=post.community,
            actor=post.owner,
            recipient=moderator,
            verb="review",
        )

        send_activity_notification_email(post, notification)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [moderator.email]

    def test_if_disabled(self, post: Post, mailoutbox: List):
        moderator = UserFactory(email_preferences=[])

        notification = Notification.objects.create(
            content_object=post,
            community=post.community,
            actor=post.owner,
            recipient=moderator,
            verb="review",
        )

        send_activity_notification_email(post, notification)
        assert len(mailoutbox) == 0


class TestSendPostDeletedEmail:
    def test_if_enabled(self, post: Post, mailoutbox: List):
        post.owner.email_preferences = ["deletes"]

        send_activity_deleted_email(post)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [post.owner.email]

    def test_if_disabled(self, post: Post, mailoutbox: List):
        post.owner.email_preferences = []

        send_activity_deleted_email(post)
        assert len(mailoutbox) == 0
