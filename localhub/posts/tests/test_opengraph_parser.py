# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..opengraph_parser import (
    parse_opengraph_data_from_html,
    parse_opengraph_data_from_url,
)


class TestParseOpengraphDataFromUrl:
    def test_if_good_response(self, mocker):
        class MockResponse:
            ok = True
            headers = {"Content-Type": "text/html; charset=utf-8"}
            content = """
<html>
<head>
<title>Hello</title>
<meta property="og:title" content="a test site">
<meta property="og:image" content="http://example.com/test.jpg">
<meta property="og:description" content="test description">
</head>
<body>
</body>
</html>"""

        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        title, image, description = parse_opengraph_data_from_url("https://google.com")
        assert title == "a test site"
        assert image == "http://example.com/test.jpg"
        assert description == "test description"

    def test_if_bad_response(self, mocker):
        class MockResponse:
            ok = False

        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        title, image, description = parse_opengraph_data_from_url("https://google.com")

        assert (title, image, description) == (None, None, None)

    def test_if_no_url(self):
        title, image, description = parse_opengraph_data_from_url(None)
        assert (title, image, description) == (None, None, None)


class TestParseOpengraphDataFromHtml:
    def test_parse_title_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:title" content="meta title">
        </head>
        </body>
        <body>
        </html>
        """
        title, _, _ = parse_opengraph_data_from_html(html)
        assert title == "meta title"

    def test_parse_title_in_twitter(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta name="twitter:title" content="meta title">
        </head>
        </body>
        <body>
        </html>
        """
        title, _, _ = parse_opengraph_data_from_html(html)
        assert title == "meta title"

    def test_parse_from_page_title(self):
        html = """
        <html>
        <head>
            <title>page title</title>
        </head>
        </body>
        <body>
        </html>
        """
        title, _, _ = parse_opengraph_data_from_html(html)
        assert title == "page title"

    def test_image_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:image" content="http://imgur.com/test.jpg">
        </head>
        </body>
        <body>
        </html>
        """
        _, image, _ = parse_opengraph_data_from_html(html)
        assert image == "http://imgur.com/test.jpg"

    def test_image_not_in_meta(self):
        html = """
        <html>
        <head>
        </head>
        </body>
        <body>
        </html>
        """
        _, image, _ = parse_opengraph_data_from_html(html)
        assert image is None

    def test_description_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:description" content="test">
        </head>
        </body>
        <body>
        </html>
        """
        _, _, description = parse_opengraph_data_from_html(html)
        assert description == "test"

    def test_description_not_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
        </head>
        </body>
        <body>
        </html>
        """
        _, _, description = parse_opengraph_data_from_html(html)
        assert description is None
