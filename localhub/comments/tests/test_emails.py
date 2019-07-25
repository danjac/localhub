# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List


from localhub.comments.emails import (
    send_comment_deleted_email,
    send_comment_notification_email,
)
from localhub.comments.models import Comment
from localhub.notifications.models import Notification
from localhub.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestSendCommentNotificationEmail:
    def test_if_enabled(self, comment: Comment, mailoutbox: List):
        moderator = UserFactory(email_preferences=["reviews"])

        notification = Notification.objects.create(
            content_object=comment,
            community=comment.community,
            actor=comment.owner,
            recipient=moderator,
            verb="review",
        )

        send_comment_notification_email(comment, notification)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [moderator.email]

    def test_if_disabled(self, comment: Comment, mailoutbox: List):
        moderator = UserFactory(email_preferences=[])

        notification = Notification.objects.create(
            content_object=comment,
            community=comment.community,
            actor=comment.owner,
            recipient=moderator,
            verb="review",
        )

        send_comment_notification_email(comment, notification)
        assert len(mailoutbox) == 0


class TestSendCommentDeletedEmail:
    def test_if_enabled(self, comment: Comment, mailoutbox: List):
        comment.owner.email_preferences = ["deletes"]

        send_comment_deleted_email(comment)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [comment.owner.email]

    def test_if_disabled(self, comment: Comment, mailoutbox: List):
        comment.owner.email_preferences = []

        send_comment_deleted_email(comment)
        assert len(mailoutbox) == 0
