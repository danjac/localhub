# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.factories import MembershipFactory

pytestmark = pytest.mark.django_db


class TestCreateMessagePermissions:
    def test_can_send_if_not_member(self, member):
        other = MembershipFactory().member
        assert not member.member.has_perm("private_messages:create_message", other)

    def test_can_send_if_anon_user(self, member, anonymous_user):
        assert not member.member.has_perm(
            "private_messages:create_message", anonymous_user
        )

    def test_can_send_if__member(self, member):
        other = MembershipFactory(community=member.community).member
        assert member.member.has_perm("private_messages:create_message", other)
