# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.users.views import (
    user_activity_stream_view,
    user_autocomplete_list_view,
    user_comment_list_view,
    user_detail_view,
    user_list_view,
    user_subscribe_view,
    user_unsubscribe_view,
)

app_name = "users"

urlpatterns = [
    path("", view=user_list_view, name="list"),
    path(
        "autocomplete/",
        view=user_autocomplete_list_view,
        name="autocomplete_list",
    ),
    path("<slug:slug>/follow/", view=user_subscribe_view, name="subscribe"),
    path(
        "<slug:slug>/unfollow/", view=user_unsubscribe_view, name="unsubscribe"
    ),
    path(
        "<slug:slug>/comments/", view=user_comment_list_view, name="comments"
    ),
    path(
        "<slug:slug>/posts/", view=user_activity_stream_view, name="activities"
    ),
    path("<slug:slug>/", view=user_detail_view, name="detail"),
]
