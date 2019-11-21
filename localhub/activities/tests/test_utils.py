# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.conf import settings
from django.urls import reverse

from localhub.posts.models import Post

from ..utils import get_breadcrumbs_for_instance, get_breadcrumbs_for_model

pytestmark = pytest.mark.django_db


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

    def test_get_breadcrumbs_for_instance_if_draft(self, post):
        post.published = None
        breadcrumbs = get_breadcrumbs_for_instance(post)
        assert len(breadcrumbs) == 3

        assert breadcrumbs[0][0] == settings.HOME_PAGE_URL
        assert breadcrumbs[1][0] == reverse("activities:drafts")
        assert breadcrumbs[2][0] == post.get_absolute_url()
