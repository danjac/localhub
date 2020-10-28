# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.mixins import LoginRequiredMixin

# Localhub
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import BaseCommentListView
from localhub.common.mixins import SearchMixin
from localhub.private_messages.mixins import SenderOrRecipientQuerySetMixin
from localhub.private_messages.views import BaseMessageListView

# Local
from .mixins import BookmarksPermissionMixin


class BookmarksStreamView(
    BookmarksPermissionMixin, LoginRequiredMixin, SearchMixin, BaseActivityStreamView
):
    template_name = "bookmarks/activities.html"
    ordering = ("-bookmarked", "-created")

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .published_or_owner(self.request.user)
            .bookmarked(self.request.user)
            .with_bookmarked_timestamp(self.request.user)
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


bookmarks_stream_view = BookmarksStreamView.as_view()


class BookmarksMessageListView(
    BookmarksPermissionMixin, SenderOrRecipientQuerySetMixin, BaseMessageListView
):
    template_name = "bookmarks/messages.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .bookmarked(self.request.user)
            .with_bookmarked_timestamp(self.request.user)
            .order_by("-bookmarked", "-created")
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


bookmarks_message_list_view = BookmarksMessageListView.as_view()


class BookmarksCommentListView(
    BookmarksPermissionMixin, LoginRequiredMixin, SearchMixin, BaseCommentListView
):
    template_name = "bookmarks/comments.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .bookmarked(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
            .with_bookmarked_timestamp(self.request.user)
            .order_by("-bookmarked", "-created")
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


bookmarks_comment_list_view = BookmarksCommentListView.as_view()
