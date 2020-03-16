# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from unittest import mock

import pytest
from pywebpush import WebPushException

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Community
from localhub.users.factories import UserFactory

from ..decorators import dispatch
from ..factories import NotificationFactory
from ..models import Notification, PushSubscription

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

        @dispatch
        def do_mention(post):
            return [notification]

        notifications = do_mention(post)

        assert len(notifications) == 1
        assert Notification.objects.count() == 1

        assert send_webpush_mock.called_once
        assert len(mailoutbox) == 1
        assert mailoutbox[0].to == [notification.recipient.email]
