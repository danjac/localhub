# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
import requests

from ..http import (
    URLResolver,
    get_domain,
    get_filename,
    get_root_url,
    is_https,
    is_image_url,
    is_url,
    resolve_url,
)


class TestURLResolver:
    def test_from_url_if_none(self):
        with pytest.raises(URLResolver.Invalid):
            URLResolver.from_url(None)

    def test_from_url_if_not_url(self):
        with pytest.raises(URLResolver.Invalid):
            URLResolver.from_url("xyz")

    def test_from_url_if_url(self):
        resolver = URLResolver.from_url("https://reddit.com")
        assert resolver.url == "https://reddit.com"

    def test_filename_if_no_path(self):
        assert URLResolver("https://reddit.com").filename == ""

    def test_filename_if_path(self):
        assert URLResolver("http://google.com/test.html").filename == "test.html"

    def test_https_if_false(self):
        assert not URLResolver("http://reddit.com").is_https

    def test_https_if_true(self):
        assert URLResolver("https://reddit.com").is_https

    def test_is_image_if_true(self):
        assert URLResolver("https://example.com/test.jpg").is_image

    def test_is_image_if_false(self):
        assert not URLResolver("https://example.com/test.txt").is_image

    def test_domain_with_path(self):
        assert URLResolver("http://google.com/test/").domain == "google.com"

    def test_domain_with_www(self):
        assert URLResolver("http://www.google.com/").domain == "google.com"

    def test_root_with_path(self):
        assert URLResolver("http://google.com/test/").root == "http://google.com"

    def test_root_with_no_path(self):
        assert URLResolver("http://google.com/").root == "http://google.com"

    def test_resolve_if_no_head_returned(self, mocker):
        class MockResponse:
            def raise_for_status(self):
                raise requests.exceptions.HTTPError()

        mocker.patch("requests.head", return_value=MockResponse())
        assert (
            URLResolver.from_url("http://google.com", resolve=True).url
            == "http://google.com"
        )

    def test_resolve_if_request_exception(self, mocker):
        mocker.patch("requests.head", side_effect=requests.RequestException)
        assert (
            URLResolver.from_url("http://google.com", resolve=True).url
            == "http://google.com"
        )

    def test_resolve_if_head_returned(self, mocker):
        class MockResponse:
            url = "https://google.com"

            def raise_for_status(self):
                pass

        mocker.patch("requests.head", return_value=MockResponse())
        assert (
            URLResolver.from_url("http://google.com", resolve=True).url
            == "https://google.com"
        )


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
        assert resolve_url("") == ""

    def test_resolve_if_no_head_returned(self, mocker):
        class MockResponse:
            def raise_for_status(self):
                raise requests.exceptions.HTTPError()

        mocker.patch("requests.head", return_value=MockResponse())
        assert resolve_url("http://google.com") == "http://google.com"

    def test_resolve_if_request_exception(self, mocker):
        mocker.patch("requests.head", side_effect=requests.RequestException)
        assert resolve_url("http://google.com") == "http://google.com"

    def test_resolve_if_head_returned(self, mocker):
        class MockResponse:
            url = "https://google.com"

            def raise_for_status(self):
                pass

        mocker.patch("requests.head", return_value=MockResponse())
        assert resolve_url("http://google.com") == "https://google.com"
