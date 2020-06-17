# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path, re_path

# Local
from . import views

app_name = "users"

USERNAME_RE = r"^(?P<username>[\w.@+-]+)/"


urlpatterns = [
    path("autocomplete/", views.user_autocomplete_list_view, name="autocomplete_list"),
    path("members/", views.member_list_view, name="member_list"),
    path("following/", views.following_user_list_view, name="following_list"),
    path("followers/", views.follower_user_list_view, name="follower_list"),
    path("blocked/", views.blocked_user_list_view, name="blocked_list"),
    re_path(
        USERNAME_RE + "likes/$", views.user_activity_likes_view, name="activity_likes"
    ),
    re_path(
        USERNAME_RE + "likes/comments/$",
        views.user_comment_likes_view,
        name="comment_likes",
    ),
    re_path(
        USERNAME_RE + "mentions/$",
        views.user_activity_mentions_view,
        name="activity_mentions",
    ),
    re_path(
        USERNAME_RE + "mentions/comments/$",
        views.user_comment_mentions_view,
        name="comment_mentions",
    ),
    re_path(USERNAME_RE + r"hovercard/$", views.user_hovercard_view, name="hovercard"),
    re_path(USERNAME_RE + r"follow/$", views.user_follow_view, name="follow"),
    re_path(USERNAME_RE + r"unfollow/$", views.user_unfollow_view, name="unfollow"),
    re_path(USERNAME_RE + r"block/$", views.user_block_view, name="block"),
    re_path(USERNAME_RE + r"unblock/$", views.user_unblock_view, name="unblock"),
    re_path(USERNAME_RE + r"comments/$", views.user_comment_list_view, name="comments"),
    re_path(USERNAME_RE + r"messages/$", views.user_message_list_view, name="messages"),
    re_path(USERNAME_RE + r"$", views.user_stream_view, name="activities"),
]
