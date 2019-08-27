# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.communities.middleware import CurrentCommunityMiddleware

pytestmark = pytest.mark.django_db


class TestCurrentCommunityMiddleware:
    def test_if_community_available(
        self, community, req_factory, get_response
    ):
        mw = CurrentCommunityMiddleware(get_response)
        req = req_factory.get("/", HTTP_HOST=community.domain)
        mw(req)
        assert req.community == community

    def test_if_no_community_available(self, req_factory, get_response):
        mw = CurrentCommunityMiddleware(get_response)
        req = req_factory.get("/", HTTP_HOST="example.com")
        mw(req)
        assert req.community.id is None
