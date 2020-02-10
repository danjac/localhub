# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestJoinRequestCreate:
    def test_if_not_member(self):
        community = CommunityFactory(allow_join_requests=True)
        user = UserFactory()
        assert user.has_perm("join_requests.create", community)

    def test_if_member(self):
        community = CommunityFactory(allow_join_requests=True)
        user = MembershipFactory(community=community).member
        assert not user.has_perm("join_requests.create", community)

    def test_if_not_allowd(self):
        community = CommunityFactory(allow_join_requests=False)
        user = MembershipFactory(community=community).member
        assert not user.has_perm("join_requests.create", community)
