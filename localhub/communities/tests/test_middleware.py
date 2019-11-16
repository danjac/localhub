# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..middleware import CurrentCommunityMiddleware

pytestmark = pytest.mark.django_db


class TestCurrentCommunityMiddleware:
    def test_if_community_available(self, community, rf, get_response):
        mw = CurrentCommunityMiddleware(get_response)
        req = rf.get("/", HTTP_HOST=community.domain)
        mw(req)
        assert req.community == community

    def test_if_no_community_available(self, rf, get_response):
        mw = CurrentCommunityMiddleware(get_response)
        req = rf.get("/", HTTP_HOST="example.com")
        mw(req)
        assert req.community.id is None
