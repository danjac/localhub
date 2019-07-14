# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.activities.views import (
    activity_search_view,
    activity_stream_view,
    activity_tag_view,
    tag_autocomplete_list_view,
    tag_subscribe_view,
    tag_unsubscribe_view,
)

app_name = "activities"

urlpatterns = [
    path("", activity_stream_view, name="stream"),
    path("search/", activity_search_view, name="search"),
    path(
        "tag-autocomplete/",
        tag_autocomplete_list_view,
        name="tag_autocomplete_list",
    ),
    path("tag/<slug:slug>/", activity_tag_view, name="tag"),
    path(
        "tag/<slug:slug>/subscribe/", tag_subscribe_view, name="subscribe_tag"
    ),
    path(
        "tag/<slug:slug>/unsubscribe/",
        tag_unsubscribe_view,
        name="unsubscribe_tag",
    ),
]
