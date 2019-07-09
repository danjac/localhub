# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List

from communikit.comments.models import Comment
from communikit.events.models import Event
from communikit.notifications.emails import send_notification_email
from communikit.notifications.models import Notification
from communikit.photos.models import Photo
from communikit.posts.models import Post
from communikit.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSendNotificationEmail:
    def test_send_emails(
        self,
        comment: Comment,
        event: Event,
        post: Post,
        photo: Photo,
        mailoutbox: List,
    ):
        recipient = UserFactory()

        for item, template_name in [
            (comment, "comments/emails/notification.txt"),
            (event, "events/emails/notification.txt"),
            (post, "posts/emails/notification.txt"),
            (photo, "photos/emails/notification.txt"),
        ]:
            notification = Notification.objects.create(
                recipient=recipient,
                verb="created",
                actor=item.owner,
                community=item.community,
                content_object=item,
            )
            send_notification_email(
                notification, "test", item.get_permalink(), template_name
            )

        assert len(mailoutbox) == 4
        assert mailoutbox[0].to == [recipient.email]
