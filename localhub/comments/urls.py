# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import (
    comment_bookmark_view,
    comment_delete_view,
    comment_detail_view,
    comment_dislike_view,
    comment_flag_view,
    comment_like_view,
    comment_list_view,
    comment_remove_bookmark_view,
    comment_reply_view,
    comment_update_view,
)

app_name = "comments"


urlpatterns = [
    path("", comment_list_view, name="list"),
    path("<int:pk>/", comment_detail_view, name="detail"),
    path("<int:pk>/~update/", comment_update_view, name="update"),
    path("<int:pk>/~delete/", comment_delete_view, name="delete"),
    path("<int:pk>/~like/", comment_like_view, name="like"),
    path("<int:pk>/~bookmark/", comment_bookmark_view, name="bookmark"),
    path(
        "<int:pk>/~bookmark/remove/",
        comment_remove_bookmark_view,
        name="remove_bookmark",
    ),
    path("<int:pk>/~dislike/", comment_dislike_view, name="dislike"),
    path("<int:pk>/~flag/", comment_flag_view, name="flag"),
    path("<int:pk>/~reply/", comment_reply_view, name="reply"),
]
