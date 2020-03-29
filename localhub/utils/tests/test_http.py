# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..http import get_domain, get_domain_url, is_https, is_image_url, is_url


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


class TestGetDomainUrl:
    def test_if_empty(self):
        assert get_domain_url("") == ""

    def test_with_path(self):
        assert get_domain_url("http://google.com/test/") == "http://google.com"


class TestGetDomain:
    def test_if_empty(self):
        assert get_domain("") == ""

    def test_with_path(self):
        assert get_domain("http://google.com/test/") == "google.com"

    def test_with_www(self):
        assert get_domain("http://www.google.com/") == "google.com"
