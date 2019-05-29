# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.events.views import (
    event_create_view,
    event_delete_view,
    event_detail_view,
    event_dislike_view,
    event_like_view,
    event_list_view,
    event_notification_mark_read_view,
    event_update_view,
)

app_name = "events"

urlpatterns = [
    path("", event_list_view, name="list"),
    path("~create", event_create_view, name="create"),
    path("<int:pk>/", event_detail_view, name="detail"),
    path("<int:pk>/~update/", event_update_view, name="update"),
    path("<int:pk>/~delete/", event_delete_view, name="delete"),
    path("<int:pk>/~like/", event_like_view, name="like"),
    path("<int:pk>/~dislike/", event_dislike_view, name="dislike"),
    path(
        "notifications/<int:pk>/~mark-read/",
        event_notification_mark_read_view,
        name="mark_notification_read",
    ),
]
