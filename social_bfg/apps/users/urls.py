# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path, re_path

# Local
from . import views

app_name = "users"

USERNAME_RE = r"^(?P<username>[\w.@+-]+)/"


def user_path(path, *args, **kwargs):
    return re_path(USERNAME_RE + path, *args, **kwargs)


urlpatterns = [
    path("autocomplete/", views.user_autocomplete_list_view, name="autocomplete_list"),
    path("members/", views.member_list_view, name="member_list"),
    path("following/", views.following_user_list_view, name="following_list"),
    path("followers/", views.follower_user_list_view, name="follower_list"),
    path("blocked/", views.blocked_user_list_view, name="blocked_list"),
    user_path("hovercard/$", views.user_hovercard_view, name="hovercard"),
    user_path("likes/$", views.user_activity_likes_view, name="activity_likes"),
    user_path("likes/comments/$", views.user_comment_likes_view, name="comment_likes"),
    user_path(
        "mentions/$", views.user_activity_mentions_view, name="activity_mentions",
    ),
    user_path(
        "mentions/comments/$",
        views.user_comment_mentions_view,
        name="comment_mentions",
    ),
    user_path(r"follow/$", views.user_follow_view, name="follow"),
    user_path(r"unfollow/$", views.user_unfollow_view, name="unfollow"),
    user_path(r"block/$", views.user_block_view, name="block"),
    user_path(r"unblock/$", views.user_unblock_view, name="unblock"),
    user_path(r"comments/$", views.user_comment_list_view, name="comments"),
    user_path(r"messages/$", views.user_message_list_view, name="messages"),
    user_path(r"$", views.user_stream_view, name="activities"),
]
