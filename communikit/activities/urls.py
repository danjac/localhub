# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.activities.views import (
    activity_profile_view,
    activity_search_view,
    activity_stream_view,
)

app_name = "activities"

urlpatterns = [
    path("", activity_stream_view, name="stream"),
    path("search/", activity_search_view, name="search"),
    path("profile/<username>/", activity_profile_view, name="profile"),
]
