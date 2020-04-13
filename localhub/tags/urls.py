# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from . import views

app_name = "activities"

urlpatterns = [
    path("", views.tag_list_view, name="tag_list"),
    path("following/", views.following_tag_list_view, name="following_tag_list",),
    path("blocked/", views.blocked_tag_list_view, name="blocked_tag_list"),
    path(
        "autocomplete/", views.tag_autocomplete_list_view, name="tag_autocomplete_list",
    ),
    path("<int:pk>/~follow/", views.tag_follow_view, name="tag_follow"),
    path("<int:pk>/~unfollow/", views.tag_unfollow_view, name="tag_unfollow",),
    path("<int:pk>/~block/", views.tag_block_view, name="tag_block"),
    path("<int:pk>/~unblock/", views.tag_unblock_view, name="tag_unblock"),
    path("<slug:slug>/", views.tag_detail_view, name="tag_detail"),
]
