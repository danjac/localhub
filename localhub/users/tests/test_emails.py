# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from typing import List


from localhub.communities.models import Community
from localhub.notifications.models import Notification
from localhub.users.emails import send_user_notification_email
from localhub.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestSendUserNotificationEmail:
    def test_if_enabled(self, community: Community, mailoutbox: List):
        follower = UserFactory()
        followed = UserFactory(email_preferences=["follows"])

        notification = Notification.objects.create(
            content_object=followed,
            community=community,
            actor=follower,
            recipient=followed,
            verb="follow",
        )

        send_user_notification_email(followed, notification)
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [followed.email]

    def test_if_disabled(self, community: Community, mailoutbox: List):
        follower = UserFactory()
        followed = UserFactory(email_preferences=[])

        notification = Notification.objects.create(
            content_object=followed,
            community=community,
            actor=follower,
            recipient=followed,
            verb="follow",
        )

        send_user_notification_email(followed, notification)
        assert len(mailoutbox) == 0
