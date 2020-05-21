# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from .. import permissions

pytestmark = pytest.mark.django_db


class TestIsCommunity:
    def test_if_active(self, api_req_factory, community):
        req = api_req_factory.get("/")
        req.community = community
        assert permissions.IsCommunity().has_permission(req, None)

    def test_if_inactive(self, api_req_factory, request_community):
        req = api_req_factory.get("/")
        req.community = request_community
        assert not permissions.IsCommunity().has_permission(req, None)


class TestIsCommunityMember:
    def test_if_member(self, api_req_factory, member):
        req = api_req_factory.get("/")
        req.community = member.community
        req.user = member.member
        assert permissions.IsCommunityMember().has_permission(req, None)

    def test_if_not_member(self, api_req_factory, community, user):
        req = api_req_factory.get("/")
        req.community = community
        req.user = user
        assert not permissions.IsCommunityMember().has_permission(req, None)


class TestIsCommunityModerator:
    def test_if_moderator(self, api_req_factory, moderator):
        req = api_req_factory.get("/")
        req.community = moderator.community
        req.user = moderator.member
        assert permissions.IsCommunityModerator().has_permission(req, None)

    def test_if_not_moderator(self, api_req_factory, community, user):
        req = api_req_factory.get("/")
        req.community = community
        req.user = user
        assert not permissions.IsCommunityModerator().has_permission(req, None)


class TestIsCommunityAdmin:
    def test_if_admin(self, api_req_factory, admin):
        req = api_req_factory.get("/")
        req.community = admin.community
        req.user = admin.member
        assert permissions.IsCommunityAdmin().has_permission(req, None)

    def test_if_not_admin(self, api_req_factory, community, user):
        req = api_req_factory.get("/")
        req.community = community
        req.user = user
        assert not permissions.IsCommunityAdmin().has_permission(req, None)
