# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings
from django.urls import reverse

from localhub.activities.utils import (
    get_breadcrumbs_for_instance,
    get_breadcrumbs_for_model,
    get_domain,
    is_url,
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
