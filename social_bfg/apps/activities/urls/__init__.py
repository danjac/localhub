# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from ..api import streams as api
from ..views import streams

app_name = "activities"

urlpatterns = [
    path("search/", streams.activity_search_view, name="search"),
    path("private/", streams.private_view, name="private"),
    path("timeline/", streams.timeline_view, name="timeline"),
    path("api/streams/default/", api.default_stream_api_view),
    path("api/streams/search/", api.search_api_view),
    path("api/streams/timeline/", api.timeline_api_view),
    path("api/streams/private/", api.private_api_view),
]
