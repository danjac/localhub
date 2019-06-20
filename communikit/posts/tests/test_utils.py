# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from pytest_mock import MockFixture

from communikit.posts.utils import fetch_title_from_url


class TestFetchTitleFromUrl:
    def test_ok(self, mocker: MockFixture):
        class Response:
            ok = True
            content = """
<html>
<head>
<title>Hello</title>
</head>
<body>
</body>
</html>"""

        mocker.patch("requests.get", lambda url: Response)
        assert fetch_title_from_url("http://google.com") == "Hello"

    def test_bad_response(self, mocker: MockFixture):
        class MockResponse:
            ok = False

        mocker.patch("requests.get", lambda url: MockResponse)
        assert fetch_title_from_url("http://google.com") is None

    def test_no_title_in_html(self, mocker: MockFixture):
        class MockResponse:
            ok = True
            content = """
<html>
<head>
</head>
<body>
</body>
</html>"""

        mocker.patch("requests.get", lambda url: MockResponse)
        assert fetch_title_from_url("http://google.com") is None
