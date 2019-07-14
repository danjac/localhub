# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from localhub.activities.models import Activity
from localhub.activities.views import BaseActivityStreamView
from localhub.comments.views import CommentListView


class LikedActivityStreamView(LoginRequiredMixin, BaseActivityStreamView):
    template_name = "likes/activities.html"

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
        return super().get_queryset_for_model(model).filter(has_liked=True)


liked_activity_stream_view = LikedActivityStreamView.as_view()


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
