# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.communities.models import Membership
from localhub.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestJoinRequestDelete:
    def test_if_sender(self, join_request):
        assert join_request.sender.has_perm("join_requests.delete", join_request)

    def test_if_admin(self, join_request):
        admin = MembershipFactory(
            community=join_request.community, role=Membership.Role.ADMIN
        ).member
        assert admin.has_perm("join_requests.delete", join_request)


class TestJoinRequestCreate:
    def test_if_anonymous(self, anonymous_user):
        community = CommunityFactory(allow_join_requests=True)
        assert not anonymous_user.has_perm("join_requests.create", community)

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
