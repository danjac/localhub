# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..opengraph import get_opengraph_from_html, get_opengraph_from_url


class TestGetOpengraphDataFromUrl:
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
        og = get_opengraph_from_url("https://google.com")
        assert og.title == "a test site"
        assert og.image == "http://example.com/test.jpg"
        assert og.description == "test description"

    def test_if_bad_response(self, mocker):
        class MockResponse:
            ok = False

        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        og = get_opengraph_from_url("https://google.com")
        assert og.is_empty

    def test_if_no_url(self):
        og = get_opengraph_from_url(None)
        assert og.is_empty


class TestGetOpengraphDataFromHtml:
    def test_get_title_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:title" content="meta title">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.title == "meta title"

    def test_get_title_in_twitter(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta name="twitter:title" content="meta title">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.title == "meta title"

    def test_get_from_header(self):
        html = """
        <html>
        <head> 
            <title>page title</title>
        </head>
        <body>
            <h1>PAGE HEADER</h1>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.title == "PAGE HEADER"

    def test_get_from_page_title(self):
        html = """
        <html>
        <head>
            <title>page title</title>
        </head>
        </body>
        <body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.title == "page title"

    def test_image_in_meta_property(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:image" content="http://imgur.com/test.jpg">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.image == "http://imgur.com/test.jpg"

    def test_image_in_meta_name(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta name="og:image" content="http://imgur.com/test.jpg">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.image == "http://imgur.com/test.jpg"

    def test_image_not_in_meta(self):
        html = """
        <html>
        <head>
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.image is None

    def test_description_in_meta_property(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta property="og:description" content="test">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.description == "test"

    def test_description_in_meta_name(self):
        html = """
        <html>
        <head>
            <title>page title</title>
            <meta name="og:description" content="test">
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.description == "test"

    def test_description_not_in_meta(self):
        html = """
        <html>
        <head>
            <title>page title</title>
        </head>
        <body>
        </body>
        </html>
        """
        og = get_opengraph_from_html(html)
        assert og.description is None
