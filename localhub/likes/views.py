# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from localhub.activities.views.streams import BaseStreamView
from localhub.activities.types import ActivityType
from localhub.comments.views import CommentListView


class LikedStreamView(LoginRequiredMixin, BaseStreamView):
    template_name = "likes/activities.html"

    def get_queryset_count_for_model(self, model: ActivityType) -> QuerySet:
        return self.filter_queryset(
            model.objects.with_has_liked(self.request.user)
        ).only("pk")

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return super().filter_queryset(queryset).filter(has_liked=True)


liked_stream_view = LikedStreamView.as_view()


class LikedCommentListView(LoginRequiredMixin, CommentListView):
    template_name = "likes/comments.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
            .filter(has_liked=True)
            .order_by("-created")
        )


liked_comment_list_view = LikedCommentListView.as_view()
