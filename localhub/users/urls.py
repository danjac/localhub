# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import (
    blocked_user_list_view,
    follower_user_list_view,
    following_user_list_view,
    member_list_view,
    user_autocomplete_list_view,
    user_block_view,
    user_comment_list_view,
    user_follow_view,
    user_message_list_view,
    user_stream_view,
    user_unblock_view,
    user_unfollow_view,
)

app_name = "users"

urlpatterns = [
    path("autocomplete/", view=user_autocomplete_list_view, name="autocomplete_list",),
    path("members/", view=member_list_view, name="member_list"),
    path("following/", view=following_user_list_view, name="following_list"),
    path("followers/", view=follower_user_list_view, name="follower_list"),
    path("blocked/", view=blocked_user_list_view, name="blocked_list"),
    path("<slug:slug>/follow/", view=user_follow_view, name="follow"),
    path("<slug:slug>/unfollow/", view=user_unfollow_view, name="unfollow"),
    path("<slug:slug>/block/", view=user_block_view, name="block"),
    path("<slug:slug>/unblock/", view=user_unblock_view, name="unblock"),
    path("<slug:slug>/comments/", view=user_comment_list_view, name="comments"),
    path("<slug:slug>/messages/", view=user_message_list_view, name="messages"),
    path("<slug:slug>/", view=user_stream_view, name="activities"),
]
