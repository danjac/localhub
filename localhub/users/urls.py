# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path, re_path

from .views.actions import (
    user_block_view,
    user_follow_view,
    user_unblock_view,
    user_unfollow_view,
)
from .views.detail import (
    user_activity_likes_view,
    user_activity_mentions_view,
    user_comment_likes_view,
    user_comment_list_view,
    user_comment_mentions_view,
    user_message_list_view,
    user_stream_view,
)
from .views.list import (
    blocked_user_list_view,
    follower_user_list_view,
    following_user_list_view,
    member_list_view,
    user_autocomplete_list_view,
)

app_name = "users"

USERNAME_RE = r"^(?P<username>[\w.@+-]+)/"


urlpatterns = [
    path("autocomplete/", view=user_autocomplete_list_view, name="autocomplete_list",),
    path("members/", view=member_list_view, name="member_list"),
    path("following/", view=following_user_list_view, name="following_list"),
    path("followers/", view=follower_user_list_view, name="follower_list"),
    path("blocked/", view=blocked_user_list_view, name="blocked_list"),
    re_path(USERNAME_RE + r"follow/$", view=user_follow_view, name="follow"),
    re_path(USERNAME_RE + r"unfollow/$", view=user_unfollow_view, name="unfollow"),
    re_path(USERNAME_RE + r"block/$", view=user_block_view, name="block"),
    re_path(USERNAME_RE + r"unblock/$", view=user_unblock_view, name="unblock"),
    re_path(USERNAME_RE + r"comments/$", view=user_comment_list_view, name="comments",),
    re_path(USERNAME_RE + r"messages/$", view=user_message_list_view, name="messages",),
    re_path(
        USERNAME_RE + "likes/$", view=user_activity_likes_view, name="activity_likes",
    ),
    re_path(
        USERNAME_RE + "likes/comments/$",
        view=user_comment_likes_view,
        name="comment_likes",
    ),
    re_path(
        USERNAME_RE + "mentions/$",
        view=user_activity_mentions_view,
        name="activity_mentions",
    ),
    re_path(
        USERNAME_RE + "mentions/comments/$",
        view=user_comment_mentions_view,
        name="comment_mentions",
    ),
    re_path(USERNAME_RE + r"$", view=user_stream_view, name="activities"),
]
