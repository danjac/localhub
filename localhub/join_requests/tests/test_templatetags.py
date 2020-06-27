# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Membership

# Local
from ..factories import JoinRequestFactory
from ..templatetags.join_requests import (
    get_pending_external_join_request_count,
    get_pending_join_request_count,
    get_sent_join_request_count,
)

pytestmark = pytest.mark.django_db


class TestGetSentJoinRequestCount:
    def test_get_sent_join_request_count(self, join_request):
        assert get_sent_join_request_count(join_request.sender) == 1


class TestGetPendingJoinRequestCount:
    def test_get_pending_join_request_count_if_admin(self, admin):
        JoinRequestFactory.create_batch(3, community=admin.community)
        assert get_pending_join_request_count(admin.member, admin.community) == 3

    def test_get_pending_join_request_count_if_not_admin(self, member):
        JoinRequestFactory.create_batch(3, community=member.community)
        assert get_pending_join_request_count(member.member, member.community) == 0

    def test_get_pending_join_request_count_if_anonymous(
        self, community, anonymous_user
    ):
        JoinRequestFactory.create_batch(3, community=community)
        assert get_pending_join_request_count(anonymous_user, community) == 0


class TestGetPendingLocalNetworkJoinRequestCount:
    def test_get_count_if_admin(self, member):
        membership = MembershipFactory(role=Membership.Role.ADMIN, member=member.member)
        JoinRequestFactory(community=membership.community)
        count = get_pending_external_join_request_count(member.member, member.community)
        assert count == 1

    def test_get_count_if_not_admin(self, member):
        membership = MembershipFactory(
            role=Membership.Role.MEMBER, member=member.member
        )
        JoinRequestFactory(community=membership.community)
        count = get_pending_external_join_request_count(member.member, member.community)
        assert count == 0

    def test_get_count_if_anonymous_user(self, community, anonymous_user):
        JoinRequestFactory(community=community)
        count = get_pending_external_join_request_count(anonymous_user, community)
        assert count == 0

    def test_get_count_if_current_community(self, admin):
        JoinRequestFactory(community=admin.community)
        count = get_pending_external_join_request_count(admin.member, admin.community)
        assert count == 0
