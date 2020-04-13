# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views.actions import (
    tag_block_view,
    tag_follow_view,
    tag_unblock_view,
    tag_unfollow_view,
)
from .views.detail import tag_detail_view
from .views.list import (
    tag_autocomplete_list_view,
    tag_list_view,
    following_tag_list_view,
    blocked_tag_list_view,
)

app_name = "hashtags"


urlpatterns = [
    path("", tag_list_view, name="list"),
    path("following/", following_tag_list_view, name="following_list",),
    path("blocked/", blocked_tag_list_view, name="blocked_list"),
    path("autocomplete/", tag_autocomplete_list_view, name="autocomplete_list"),
    path("<int:pk>/~follow/", tag_follow_view, name="follow"),
    path("<int:pk>/~unfollow/", tag_unfollow_view, name="unfollow",),
    path("<int:pk>/~block/", tag_block_view, name="block"),
    path("<int:pk>/~unblock/", tag_unblock_view, name="unblock"),
    path("<slug:slug>/", tag_detail_view, name="detail"),
]
