# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from vanilla import DetailView

from ..models import Comment
from .mixins import CommentQuerySetMixin


class CommentDetailView(CommentQuerySetMixin, DetailView):
    model = Comment

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_deleted(self.request.user)
            .select_related("editor")
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_flags(self):
        return (
            self.object.get_flags()
            .select_related("user")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    def get_replies(self):
        if self.object.deleted:
            return self.get_queryset().none()
        return (
            self.get_queryset()
            .filter(parent=self.object)
            .prefetch_related("content_object")
            .order_by("created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()
        data.update(
            {
                "replies": self.get_replies(),
                "content_object": self.object.get_content_object(),
                "parent": self.object.get_parent(),
            }
        )
        return data


comment_detail_view = CommentDetailView.as_view()
