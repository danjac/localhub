# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List, Any

from django.conf import settings

from communikit.posts.emails import send_notification_email
from communikit.posts.models import Post, PostNotification

pytestmark = pytest.mark.django_db


class TestSendNotificationEmail:
    def test_send_if_mentioned(
        self, user: settings.AUTH_USER_MODEL, post: Post, mailoutbox: List[Any]
    ):

        notification = PostNotification.objects.create(
            post=post, recipient=user, verb="mentioned"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == "You have been mentioned in a post"
        assert (
            f"User {post.owner.username} has mentioned you in a post"
            in mail.body
        )

    def test_send_if_created(
        self, user: settings.AUTH_USER_MODEL, post: Post, mailoutbox: List[Any]
    ):

        notification = PostNotification.objects.create(
            post=post, recipient=user, verb="created"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has published a post to the {post.community.name} community"  # noqa
        )
        assert (
            f"User {post.owner.username} has published a post"
            in mail.body
        )

    def test_send_if_updated(
        self, user: settings.AUTH_USER_MODEL, post: Post, mailoutbox: List[Any]
    ):

        notification = PostNotification.objects.create(
            post=post, recipient=user, verb="updated"
        )
        send_notification_email(notification)
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert (
            mail.subject
            == f"A user has edited their post in the {post.community.name} community"  # noqa
        )
        assert (
            f"User {post.owner.username} has edited a post"
            in mail.body
        )
