# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from vanilla import ListView

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import BaseCommentListView
from localhub.private_messages.views import SenderOrRecipientQuerySetMixin


class BookmarksStreamView(BaseActivityStreamView):
    template_name = "bookmarks/activities.html"
    ordering = ("-bookmarked", "-created")

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects.bookmarked(self.request.user))

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .bookmarked(self.request.user)
            .with_bookmarked_timestamp(self.request.user)
        )


bookmarks_stream_view = BookmarksStreamView.as_view()


class BookmarksCommentListView(BaseCommentListView):
    template_name = "bookmarks/comments.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .bookmarked(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
            .with_bookmarked_timestamp(self.request.user)
            .order_by("-bookmarked", "-created")
        )


bookmarks_comment_list_view = BookmarksCommentListView.as_view()


class BookmarksMessageListView(SenderOrRecipientQuerySetMixin, ListView):

    template_name = "bookmarks/messages.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .bookmarked(self.request.user)
            .with_bookmarked_timestamp(self.request.user)
            .order_by("-bookmarked", "-created")
        )


bookmarks_message_list_view = BookmarksMessageListView.as_view()
