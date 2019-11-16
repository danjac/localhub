# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..templatetags import pagination_url


class TestPaginationUrl:
    def test_append_page_number_to_querystring(self, rf):

        req = rf.get("/search/", {"q": "test"})
        url = pagination_url({"request": req}, 5)
        assert url.startswith("/search/?")
        assert "q=test" in url
        assert "page=5" in url
