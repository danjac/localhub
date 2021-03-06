# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from .views import liked_comment_list_view, liked_stream_view

app_name = "likes"

urlpatterns = [
    path("", liked_stream_view, name="activities"),
    path("comments/", liked_comment_list_view, name="comments"),
]
