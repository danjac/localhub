# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

from django.utils import timezone

import pytest

from localhub.events.factories import EventFactory
from localhub.events.models import Event
from localhub.photos.factories import PhotoFactory
from localhub.photos.models import Photo
from localhub.polls.models import Poll
from localhub.posts.factories import PostFactory
from localhub.posts.models import Post

from ..utils import (
    get_activity_model,
    get_activity_models,
    get_activity_models_dict,
    get_activity_queryset_count,
    get_activity_querysets,
    load_objects,
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

    def test_get_activity_models_dict(self):
        d = get_activity_models_dict()
        assert d == {
            "event": Event,
            "poll": Poll,
            "photo": Photo,
            "post": Post,
        }

    def test_get_activity_model(self):
        assert get_activity_model("post") == Post

    def test_get_activity_model_if_invalid(self):
        with pytest.raises(KeyError):
            get_activity_model("something")


class TestGetActivityQuerysets:
    def test_get_activity_querysets(self):
        post = PostFactory(published=timezone.now() - timedelta(days=1))
        event = EventFactory(published=timezone.now() - timedelta(days=3))
        PhotoFactory(published=None)

        qs, querysets = get_activity_querysets(
            lambda model: model.objects.filter(published__isnull=False),
            ordering="-published",
        )

        assert len(qs) == 2
        assert len(querysets) == 4

        items = load_objects(qs, querysets)
        assert len(items) == 2

        assert items[0]["pk"] == post.id
        assert items[0]["object"] == post
        assert items[0]["object_type"] == "post"

        assert items[1]["pk"] == event.id
        assert items[1]["object"] == event
        assert items[1]["object_type"] == "event"


class TestGetActivityQuerysetCount:
    def test_get_activity_queryset_count(self):
        PostFactory()
        EventFactory()

        assert get_activity_queryset_count(lambda model: model.objects.all()) == 2
