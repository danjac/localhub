# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from localhub.communities.models import Membership
from localhub.messageboard.templatetags.messageboard_tags import (
    get_unread_messages_count,
)
from localhub.messageboard.tests.factories import (
    MessageFactory,
    MessageRecipientFactory,
)

pytestmark = pytest.mark.django_db


class TestGetUnreadMessagesCount:
    def test_anonymous(self, req_factory: RequestFactory):
        request = req_factory.get("/")
        request.user = AnonymousUser()
        assert get_unread_messages_count({"request": request}) == 0

    def test_authenticated(
        self, req_factory: RequestFactory, member: Membership
    ):
        request = req_factory.get("/")
        request.user = member.member
        request.community = member.community
        message = MessageFactory(community=member.community)
        MessageRecipientFactory(message=message, recipient=member.member)
        assert get_unread_messages_count({"request": request}) == 1
