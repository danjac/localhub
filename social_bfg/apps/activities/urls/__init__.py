# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from ..api import streams as api

app_name = "activities"

urlpatterns = [
    path("default/", api.default_stream_api_view),
    path("search/", api.search_api_view),
    path("timeline/", api.timeline_api_view),
    path("private/", api.private_api_view),
]
