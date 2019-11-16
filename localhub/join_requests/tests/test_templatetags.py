# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership

from ..factories import JoinRequestFactory
from ..templatetags.join_requests_tags import (
    get_pending_join_request_count,
    get_pending_local_network_join_request_count,
)

pytestmark = pytest.mark.django_db


class TestGetPendingJoinRequestCount:
    def test_get_pending_join_request_count(self, community):
        JoinRequestFactory.create_batch(3, community=community)
        assert get_pending_join_request_count(community) == 3


class TestGetPendingLocalNetworkJoinRequestCount:
    def test_get_count_if_admin(self, member):
        membership = MembershipFactory(
            role=Membership.ROLES.admin, member=member.member
        )
        JoinRequestFactory(community=membership.community)
        count = get_pending_local_network_join_request_count(
            {}, member.member, member.community
        )
        assert count == 1

    def test_get_count_if_not_admin(self, member):
        membership = MembershipFactory(
            role=Membership.ROLES.member, member=member.member
        )
        JoinRequestFactory(community=membership.community)
        count = get_pending_local_network_join_request_count(
            {}, member.member, member.community
        )
        assert count == 0

    def test_get_count_if_current_community(self, admin):
        JoinRequestFactory(community=admin.community)
        count = get_pending_local_network_join_request_count(
            {}, admin.member, admin.community
        )
        assert count == 0
