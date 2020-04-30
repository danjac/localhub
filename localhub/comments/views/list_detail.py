# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.views.generic import DetailView, ListView

from localhub.common.views import SearchMixin

from ..models import Comment
from .mixins import CommentQuerySetMixin


class BaseCommentListView(CommentQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked_users(self.request.user)
            .exclude_deleted()
            .with_common_related()
        )


class CommentListView(SearchMixin, BaseCommentListView):

    template_name = "comments/comment_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


comment_list_view = CommentListView.as_view()


class CommentDetailView(CommentQuerySetMixin, DetailView):
    model = Comment

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_deleted(self.request.user)
            .with_common_related()
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
            .select_related("user", "community")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    def get_replies(self):
        if self.object.deleted:
            return self.get_queryset().none()
        return self.get_queryset().filter(parent=self.object).order_by("created")

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
            }
        )
        return data


comment_detail_view = CommentDetailView.as_view()
