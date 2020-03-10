# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.notifications.models import Notification
from localhub.users.factories import UserFactory

from ..notifications import send_comment_deleted_email, send_comment_notification_email

pytestmark = pytest.mark.django_db


class TestSendCommentNotificationEmail:
    def test_send_notification(self, comment, mailoutbox):
        moderator = UserFactory(send_email_notifications=True)

        notification = Notification.objects.create(
            content_object=comment,
            community=comment.community,
            actor=comment.owner,
            recipient=moderator,
            verb="moderator_review_request",
        )

        send_comment_notification_email(comment, notification)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [moderator.email]


class TestSendCommentDeletedEmail:
    def test_if_enabled(self, comment, mailoutbox):
        comment.owner.send_email_notifications = True

        send_comment_deleted_email(comment)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [comment.owner.email]

    def test_if_disabled(self, comment, mailoutbox):
        comment.owner.send_email_notifications = False

        send_comment_deleted_email(comment)
        assert len(mailoutbox) == 0
