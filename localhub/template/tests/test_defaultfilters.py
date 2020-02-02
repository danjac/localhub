# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..defaultfilters import domain, from_dictkey, html_unescape, url_to_img


class TestUrlToImg:
    def test_if_image(self):
        url = "https://somedomain.org/test.jpg"
        assert url_to_img(url) == (
            '<a href="https://somedomain.org/test.jpg" rel="nofollow"'
            '><img src="https://somedomain.org/test.jpg" '
            'alt="somedomain.org"></a>'
        )

    def test_if_unsafe_image(self):
        url = "http://somedomain.org/test.jpg"
        assert url_to_img(url) == ""

    def test_if_image_no_link(self):
        url = "https://somedomain.org/test.jpg"
        assert url_to_img(url, False) == (
            '<img src="https://somedomain.org/test.jpg" alt="somedomain.org">'
        )

    def test_if_not_image(self):
        url = "https://somedomain.org/"
        assert url_to_img(url) == ""

    def test_if_not_url(self):
        text = "<div></div>"
        assert url_to_img(text) == "<div></div>"


class TestHtmlUnescape:
    def test_html_unescape(self):
        text = "this is &gt; that"
        assert html_unescape(text) == "this is > that"


class TestDomain:
    def test_if_not_valid_url(self):
        assert domain("<div />") == "<div />"

    def test_if_valid_url(self):
        assert domain("http://reddit.com").endswith(">reddit.com</a>")

    def test_if_www(self):
        assert domain("http://www.reddit.com").endswith(">reddit.com</a>")


class TestFromDictkey:
    def test_is_dict(self):
        d = {"1": "3"}

        assert from_dictkey(d, "1") == "3"

    def test_is_none(self):
        assert from_dictkey(None, "1") is None
