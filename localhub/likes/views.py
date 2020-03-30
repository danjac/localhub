# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import BaseCommentListView


class LikedStreamView(BaseActivityStreamView):
    template_name = "likes/activities.html"
    ordering = ("-liked", "-created")

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects.liked(self.request.user))

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).with_liked_timestamp(self.request.user)


liked_stream_view = LikedStreamView.as_view()


class LikedCommentListView(BaseCommentListView):
    template_name = "likes/comments.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .with_liked_timestamp(self.request.user)
            .order_by("-liked", "-created")
        )


liked_comment_list_view = LikedCommentListView.as_view()
