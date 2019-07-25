# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Community, Membership
from localhub.messageboard.templatetags.messageboard_tags import (
    get_unread_message_count,
)
from localhub.messageboard.tests.factories import (
    MessageFactory,
    MessageRecipientFactory,
)

pytestmark = pytest.mark.django_db


class TestGetUnreadMessageCount:
    def test_anonymous(self, community: Community):
        assert get_unread_message_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member: Membership):
        message = MessageFactory(community=member.community)
        MessageRecipientFactory(message=message, recipient=member.member)
        assert get_unread_message_count(member.member, member.community) == 1
