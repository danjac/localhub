# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import streams, tags

app_name = "activities"

urlpatterns = [
    path("drafts/", streams.drafts_view, name="drafts"),
    path("search/", streams.search_view, name="search"),
    path("timeline/", streams.timeline_view, name="timeline"),
    path("tags/", tags.tag_list_view, name="tag_list"),
    path("tags/following/", tags.following_tag_list_view, name="following_tag_list",),
    path("tags/blocked/", tags.blocked_tag_list_view, name="blocked_tag_list"),
    path(
        "tags/autocomplete/",
        tags.tag_autocomplete_list_view,
        name="tag_autocomplete_list",
    ),
    path("tags/<int:pk>/~follow/", tags.tag_follow_view, name="tag_follow"),
    path("tags/<int:pk>/~unfollow/", tags.tag_unfollow_view, name="tag_unfollow",),
    path("tags/<int:pk>/~block/", tags.tag_block_view, name="tag_block"),
    path("tags/<int:pk>/~unblock/", tags.tag_unblock_view, name="tag_unblock"),
    path("tags/<slug:slug>/", tags.tag_detail_view, name="tag_detail"),
]
