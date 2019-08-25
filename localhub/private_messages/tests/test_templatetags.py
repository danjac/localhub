# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.communities.models import Community, Membership
from localhub.private_messages.templatetags.private_messages_tags import (
    get_unread_message_count,
)
from localhub.private_messages.tests.factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestGetUnreadMessageCount:
    def test_anonymous(self, community: Community):
        assert get_unread_message_count(AnonymousUser(), community) == 0

    def test_authenticated(self, member: Membership):
        MessageFactory(community=member.community, recipient=member.member)
        assert get_unread_message_count(member.member, member.community) == 1
