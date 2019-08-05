# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.activities.templatetags.activities_tags import domain


class TestDomain:
    def test_if_not_valid_url(self):
        assert domain("<div />") == "<div />"

    def test_if_valid_url(self):
        assert (
            domain("http://reddit.com")
            == '<a href="http://reddit.com" rel="nofollow">reddit.com</a>'
        )

    def test_if_www(self):
        assert (
            domain("http://www.reddit.com")
            == '<a href="http://www.reddit.com" rel="nofollow">reddit.com</a>'
        )
