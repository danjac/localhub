# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.users.views import (
    follower_user_list_view,
    following_user_list_view,
    user_autocomplete_list_view,
    user_comment_list_view,
    user_detail_view,
    user_follow_view,
    user_list_view,
    user_stream_view,
    user_unfollow_view,
)

app_name = "users"

urlpatterns = [
    path("", view=user_list_view, name="list"),
    path(
        "autocomplete/",
        view=user_autocomplete_list_view,
        name="autocomplete_list",
    ),
    path("following/", view=following_user_list_view, name="following_list"),
    path("followers/", view=follower_user_list_view, name="follower_list"),
    path("<slug:slug>/follow/", view=user_follow_view, name="follow"),
    path("<slug:slug>/unfollow/", view=user_unfollow_view, name="unfollow"),
    path("<slug:slug>/about/", view=user_detail_view, name="detail"),
    path(
        "<slug:slug>/comments/", view=user_comment_list_view, name="comments"
    ),
    path("<slug:slug>/", view=user_stream_view, name="activities"),
]
