# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List, no_type_check

from localhub.comments.models import Comment
from localhub.events.models import Event
from localhub.notifications.emails import send_notification_email
from localhub.notifications.models import Notification
from localhub.photos.models import Photo
from localhub.posts.models import Post
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestSendNotificationEmail:
    @no_type_check
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
