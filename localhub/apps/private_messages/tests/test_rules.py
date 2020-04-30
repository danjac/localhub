# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.apps.communities.factories import CommunityFactory

pytestmark = pytest.mark.django_db


class TestCreateMessagePermissions:
    def test_can_send_if_not_member(self, user):
        assert not user.has_perm("private_messages.create_message", CommunityFactory())

    def test_can_send_if_member(self, member):
        assert member.member.has_perm(
            "private_messages.create_message", member.community
        )
