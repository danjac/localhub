# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.comments.emails import send_comment_notification_email
from localhub.comments.models import Comment
from localhub.comments.push import send_comment_notification_push
from localhub.notifications.models import Notification


def send_comment_notifications(comment: Comment, notification: Notification):
    send_comment_notification_push(comment, notification)
    send_comment_notification_email(comment, notification)
