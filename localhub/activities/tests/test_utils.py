# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.urls import reverse

from localhub.activities.utils import (
    get_breadcrumbs_for_instance,
    get_breadcrumbs_for_model,
    get_domain,
    is_image_url,
    is_url,
    slugify_unicode,
)
from localhub.posts.models import Post


pytestmark = pytest.mark.django_db


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


class TestGetBreadcrumbs:
    def test_get_breadcrumbs_for_model(self):
        breadcrumbs = get_breadcrumbs_for_model(Post)
        assert len(breadcrumbs) == 2

        assert breadcrumbs[0][0] == settings.HOME_PAGE_URL
        assert breadcrumbs[1][0] == reverse("posts:list")

    def test_get_breadcrumbs_for_instance(self, post):
        breadcrumbs = get_breadcrumbs_for_instance(post)
        assert len(breadcrumbs) == 3

        assert breadcrumbs[0][0] == settings.HOME_PAGE_URL
        assert breadcrumbs[1][0] == reverse("posts:list")
        assert breadcrumbs[2][0] == post.get_absolute_url()


class TestSlugifyUnicode:
    def test_slugify_unicode_if_plain_ascii(self):
        assert slugify_unicode("test") == "test"

    def test_slugify_unicode_if_unicode(self):
        assert slugify_unicode("Байконур") == "baikonur"
