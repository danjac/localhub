# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import (
    bookmarks_comment_list_view,
    bookmarks_message_list_view,
    bookmarks_stream_view,
)

app_name = "bookmarks"

urlpatterns = [
    path("", bookmarks_stream_view, name="activities"),
    path("comments/", bookmarks_comment_list_view, name="comments"),
    path("messages/", bookmarks_message_list_view, name="messages"),
]
