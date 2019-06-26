# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.activities.views import (
    activity_search_view,
    activity_stream_view,
    activity_tag_view,
)

app_name = "activities"

urlpatterns = [
    path("", activity_stream_view, name="stream"),
    path("search/", activity_search_view, name="search"),
    path("tag/<slug:tag>/", activity_tag_view, name="tag"),
]
