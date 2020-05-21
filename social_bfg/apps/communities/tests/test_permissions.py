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
