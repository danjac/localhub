# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests

from ..http import (
    get_domain,
    get_root_url,
    get_filename,
    is_https,
    is_image_url,
    is_url,
    resolve_url,
    URLResolver,
)


class TestURLResolver:
    def test_is_valid_if_none(self):
        assert not URLResolver(None).is_valid

    def test_is_valid_if_not_url(self):
        assert not URLResolver("xyz").is_valid

    def test_is_valid_if_url(self):
        assert URLResolver("https://reddit.com").is_valid

    def test_filename_if_not_url(self):
        assert URLResolver("").filename is None

    def test_filename_if_no_path(self):
        assert URLResolver("https://reddit.com").filename == ""

    def test_filename_if_path(self):
        assert URLResolver("http://google.com/test.html").filename == "test.html"

    def test_https_if_not_url(self):
        assert not URLResolver("reddit").is_https

    def test_https_if_false(self):
        assert not URLResolver("http://reddit.com").is_https

    def test_https_if_true(self):
        assert URLResolver("https://reddit.com").is_https

    def test_is_image_if_not_url(self):
        assert not URLResolver("example").is_image

    def test_is_image_if_true(self):
        assert URLResolver("https://example.com/test.jpg").is_image

    def test_is_image_if_false(self):
        assert not URLResolver("https://example.com/test.txt").is_image

    def test_domain_if_not_url(self):
        assert URLResolver("").domain is None

    def test_domain_with_path(self):
        assert URLResolver("http://google.com/test/").domain == "google.com"

    def test_domain_with_www(self):
        assert URLResolver("http://www.google.com/").domain == "google.com"

    def test_root_if_not_url(self):
        assert URLResolver("").root is None

    def test_root_with_path(self):
        assert URLResolver("http://google.com/test/").root == "http://google.com"

    def test_root_with_no_path(self):
        assert URLResolver("http://google.com/").root == "http://google.com"

    def test_resolve_if_not_url(self):
        assert URLResolver("").resolve() is None

    def test_resolve_if_no_head_returned(self, mocker):
        class MockResponse:
            ok = False

        mocker.patch("requests.head", return_value=MockResponse)
        resolver = URLResolver("http://google.com")

        assert resolver.resolve() == "http://google.com"
        assert resolver.url == "http://google.com"

    def test_resolve_if_request_exception(self, mocker):
        mocker.patch("requests.head", side_effect=requests.RequestException)
        resolver = URLResolver("http://google.com")

        assert resolver.resolve() == "http://google.com"
        assert resolver.url == "http://google.com"

    def test_resolve_if_head_returned(self, mocker):
        class MockResponse:
            ok = True
            url = "https://google.com"

        mocker.patch("requests.head", return_value=MockResponse)
        resolver = URLResolver("http://google.com")

        assert resolver.resolve() == "https://google.com"
        assert resolver.url == "https://google.com"


class TestGetFilename:
    def test_get_filename_if_empty(self):
        assert get_filename("") is None

    def test_get_filename_if_no_path(self):
        assert get_filename("https://reddit.com") == ""

    def test_get_filename_if_path(self):
        assert get_filename("http://google.com/test.html") == "test.html"


class TestIsHttps:
    def test_if_not_url(self):
        assert not is_https("reddit")

    def test_if_not_https(self):
        assert not is_https("http://reddit.com")

    def test_if_https(self):
        assert is_https("https://reddit.com")


class TestIsUrl:
    def test_if_none(self):
        assert not is_url(None)

    def test_if_not_url(self):
        assert not is_url("xyz")

    def test_if_url(self):
        assert is_url("https://reddit.com")


class TestIsImageUrl:
    def test_if_is_image(self):
        assert is_image_url("https://example.com/test.jpg")

    def test_if_is_not_image(self):
        assert not is_image_url("https://example.com/test.txt")


class TestGetRootUrl:
    def test_if_empty(self):
        assert get_root_url("") is None

    def test_with_path(self):
        assert get_root_url("http://google.com/test/") == "http://google.com"


class TestGetDomain:
    def test_if_empty(self):
        assert get_domain("") is None

    def test_with_path(self):
        assert get_domain("http://google.com/test/") == "google.com"

    def test_with_www(self):
        assert get_domain("http://www.google.com/") == "google.com"


class TestResolveUrl:
    def test_resolve_if_not_url(self):
        assert resolve_url("") is None

    def test_resolve_if_no_head_returned(self, mocker):
        class MockResponse:
            ok = False

        mocker.patch("requests.head", return_value=MockResponse)
        assert resolve_url("http://google.com") == "http://google.com"

    def test_resolve_if_request_exception(self, mocker):
        mocker.patch("requests.head", side_effect=requests.RequestException)
        assert resolve_url("http://google.com") == "http://google.com"

    def test_resolve_if_head_returned(self, mocker):
        class MockResponse:
            ok = True
            url = "https://google.com"

        mocker.patch("requests.head", return_value=MockResponse)
        assert resolve_url("http://google.com") == "https://google.com"
