# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse

from localhub.posts.models import Post

from ..utils import (
    extract_hashtags,
    get_breadcrumbs_for_instance,
    get_breadcrumbs_for_model,
    linkify_hashtags,
)

pytestmark = pytest.mark.django_db


class TestGetBreadcrumbs:
    def test_get_breadcrumbs_for_model(self):
        breadcrumbs = get_breadcrumbs_for_model(Post)
        assert len(breadcrumbs) == 1

        assert breadcrumbs[0][0] == reverse("posts:list")

    def test_get_breadcrumbs_for_instance(self, post):
        breadcrumbs = get_breadcrumbs_for_instance(post)
        assert len(breadcrumbs) == 2

        assert breadcrumbs[0][0] == reverse("posts:list")
        assert breadcrumbs[1][0] == post.get_absolute_url()

    def test_get_breadcrumbs_for_instance_if_draft(self, post):
        post.published = None
        breadcrumbs = get_breadcrumbs_for_instance(post)
        assert len(breadcrumbs) == 2

        assert breadcrumbs[0][0] == reverse("activities:drafts")
        assert breadcrumbs[1][0] == post.get_absolute_url()


class TestExtractHashtags:
    def test_extract(self):
        content = "tags: #coding #opensource #Coding2019 #kesä"
        assert extract_hashtags(content) == {
            "coding",
            "opensource",
            "coding2019",
            "kesä",
        }


class TestLinkifyHashtags:
    def test_linkify(self):
        content = "tags: #coding #opensource #Coding2019 #kesä"
        replaced = linkify_hashtags(content)
        assert (
            replaced == 'tags: <a href="/tags/coding/">#coding</a>'
            ' <a href="/tags/opensource/">#opensource</a>'
            ' <a href="/tags/coding2019/">#Coding2019</a>'
            ' <a href="/tags/kesa/">#kesä</a>'
        )
