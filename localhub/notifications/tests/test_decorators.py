# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import MembershipFactory

# Local
from ..decorators import notify
from ..models import Notification

pytestmark = pytest.mark.django_db


class TestDispatch:
    def test_dispatch(self, post, mailoutbox, send_webpush_mock):
        notification = Notification(
            community=post.community,
            verb="mention",
            actor=post.owner,
            content_object=post,
            recipient=MembershipFactory(community=post.community).member,
        )

        @notify
        def do_mention(post):
            return [notification]

        notifications = do_mention(post)

        assert len(notifications) == 1
        assert Notification.objects.count() == 1

        assert send_webpush_mock.delay.called_once
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [notification.recipient.email]

    def test_dispatch_if_single_instance(self, post, mailoutbox, send_webpush_mock):
        notification = Notification(
            community=post.community,
            verb="mention",
            actor=post.owner,
            content_object=post,
            recipient=MembershipFactory(community=post.community).member,
        )

        @notify
        def do_mention(post):
            return notification

        notifications = do_mention(post)

        assert len(notifications) == 1
        assert Notification.objects.count() == 1

        assert send_webpush_mock.delay.called_once
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [notification.recipient.email]
