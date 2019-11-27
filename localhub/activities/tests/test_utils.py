# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.conf import settings
from django.urls import reverse

from localhub.events.factories import EventFactory
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.polls.models import Poll
from localhub.posts.factories import PostFactory
from localhub.posts.models import Post

from ..utils import (
    get_activity_models,
    get_breadcrumbs_for_instance,
    get_breadcrumbs_for_model,
    get_combined_activity_queryset,
    get_combined_activity_queryset_count,
)

pytestmark = pytest.mark.django_db


class TestGetActivityModels:
    def test_get_activity_models(self):
        models = get_activity_models()
        assert len(models) == 4
        assert Event in models
        assert Poll in models
        assert Photo in models
        assert Post in models


class TestGetCombinedActivityQueryset:
    def test_get_combined_activity_queryset(self):
        PostFactory()
        EventFactory()

        qs = get_combined_activity_queryset(lambda qs: qs.only("pk", "title"))

        assert len(qs) == 2


class TestGetCombinedActivityQuerysetCount:
    def test_get_combined_activity_queryset_count(self):
        PostFactory()
        EventFactory()

        assert get_combined_activity_queryset_count(lambda qs: qs.only("pk")) == 2


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
