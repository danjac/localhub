# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from . import views

app_name = "comments"


urlpatterns = [
    path("", views.comment_list_view, name="list"),
    path("<int:pk>/", views.comment_detail_view, name="detail"),
    path("<int:pk>/~update/", views.comment_update_view, name="update"),
    path("<int:pk>/~delete/", views.comment_delete_view, name="delete"),
    path("<int:pk>/~bookmark/", views.comment_bookmark_view, name="bookmark"),
    path(
        "<int:pk>/~bookmark/remove/",
        views.comment_bookmark_view,
        name="remove_bookmark",
        kwargs={"remove": True},
    ),
    path("<int:pk>/~like/", views.comment_like_view, name="like"),
    path(
        "<int:pk>/~dislike/",
        views.comment_like_view,
        name="dislike",
        kwargs={"remove": True},
    ),
    path("<int:pk>/~flag/", views.comment_flag_view, name="flag"),
    path("<int:pk>/~reply/", views.comment_reply_view, name="reply"),
]
