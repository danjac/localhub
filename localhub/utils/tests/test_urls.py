# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..urls import get_domain, is_image_url, is_url


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


class TestGetDomain:
    def test_if_empty(self):
        assert get_domain("") is None

    def test_with_path(self):
        assert get_domain("http://google.com/test/") == "google.com"

    def test_with_www(self):
        assert get_domain("http://www.google.com/") == "google.com"
