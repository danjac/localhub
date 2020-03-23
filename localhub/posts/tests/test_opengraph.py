# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from ..opengraph import Opengraph


class TestOpengraphFromUrl:
    def test_if_good_response_with_head_different_url(self, mocker):
        class MockHeadResponse:
            ok = True
            url = "https://google.com"

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

        mocker.patch("requests.head", lambda url, **kwargs: MockHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)

        og = Opengraph.from_url("http://google.com")

        assert og.url == "https://google.com"
        assert og.title == "a test site"
        assert og.image == "http://example.com/test.jpg"
        assert og.description == "test description"

    def test_if_good_response_no_header(self, mocker):
        class MockBadHeadResponse:
            ok = False

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

        mocker.patch("requests.head", lambda url, **kwargs: MockBadHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)
        og = Opengraph.from_url("https://google.com")

        assert og.url == "https://google.com"
        assert og.title == "a test site"
        assert og.image == "http://example.com/test.jpg"
        assert og.description == "test description"

    def test_if_bad_response(self, mocker):
        class MockHeadResponse:
            ok = True
            url = "https://google.com"

        class MockResponse:
            ok = False

        mocker.patch("requests.head", lambda url, **kwargs: MockHeadResponse)
        mocker.patch("requests.get", lambda url, **kwargs: MockResponse)

        og = Opengraph.from_url("https://google.com")
        assert og.url == "https://google.com"
        assert og.title is None
        assert og.image is None
        assert og.description is None

    def test_title_from_og(self):
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
        og = Opengraph("http://google.com").parse_html(html)
        assert og.title == "meta title"

    def test_title_from_twitter(self):
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
        og = Opengraph("http://google.com").parse_html(html)
        assert og.title == "meta title"

    def test_title_from_h1(self):
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
        og = Opengraph("http://google.com").parse_html(html)
        assert og.title == "PAGE HEADER"

    def test_title_from_title_tag(self):
        html = """
        <html>
        <head>
            <title>page title</title>
        </head>
        </body>
        <body>
        </html>
        """
        og = Opengraph("http://google.com").parse_html(html)
        assert og.title == "page title"

    def test_title_from_domain(self):
        html = """
        <html>
        <head>
        </head>
        </body>
        <body>
        </html>
        """
        og = Opengraph("http://google.com").parse_html(html)
        assert og.title == "google.com"

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
        og = Opengraph("http://google.com").parse_html(html)
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
        og = Opengraph("http://google.com").parse_html(html)
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
        og = Opengraph("http://google.com").parse_html(html)
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
        og = Opengraph("http://google.com").parse_html(html)
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
        og = Opengraph("http://google.com").parse_html(html)
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
        og = Opengraph("http://google.com").parse_html(html)
        assert og.description is None
