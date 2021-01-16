# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Localhub
from localhub.activities.views.streams import render_activity_stream
from localhub.comments.views import BaseCommentListView
from localhub.common.mixins import SearchMixin
from localhub.communities.decorators import community_required
from localhub.private_messages.mixins import SenderOrRecipientQuerySetMixin
from localhub.private_messages.views import BaseMessageListView

# Local
from .mixins import BookmarksPermissionMixin


@community_required
@login_required
def bookmarks_stream_view(request):

    search = request.GET.get("search", None)

    def _filter_queryset(qs):
        qs = (
            qs.for_community(request.community)
            .published_or_owner(request.user)
            .bookmarked(request.user)
            .with_bookmarked_timestamp(request.user)
        )

        if search:
            qs = qs.search(qs)
        return qs

    return render_activity_stream(
        request,
        _filter_queryset,
        "bookmarks/activities.html",
        ordering=("-rank", "-bookmarked") if search else ("-bookmarked", "-created"),
        extra_context={"search": search},
    )


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
