# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import CommunitySerializer, MembershipSerializer

pytestmark = pytest.mark.django_db


class TestCommunitySerializer:
    def test_serialize_community(self, community):
        data = CommunitySerializer(community).data
        assert data["name"] == community.name
        assert data["absolute_url"] == "http://testserver"


class TestMembershipSerializer:
    def test_serialize_membership(self, member):
        data = MembershipSerializer(member).data
        assert data["member"]["username"] == member.member.username
        assert data["role"] == "member"
        assert data["active"]
