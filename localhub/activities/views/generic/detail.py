# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from vanilla import DetailView

from localhub.comments.forms import CommentForm
from localhub.pagination import PresetCountPaginator

from .mixins import ActivityTemplateMixin, ActivityQuerySetMixin


class ActivityDetailView(ActivityQuerySetMixin, ActivityTemplateMixin, DetailView):
    paginator_class = PresetCountPaginator
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE
    page_kwarg = "page"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()

        data["comments"] = self.get_comments_page(self.get_comments())
        if self.request.user.has_perm("activities.create_comment", self.object):
            data["comment_form"] = CommentForm()

        data["reshares"] = self.get_reshares()
        return data

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("editor")
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
        )

    def get_flags(self):
        return (
            self.object.get_flags()
            .select_related("user")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    def get_reshares(self):
        return (
            self.object.reshares.for_community(self.request.community)
            .exclude_blocked_users(self.request.user)
            .select_related("owner")
            .order_by("-created")
        )

    def get_comments(self):
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.user, self.request.community)
            .for_community(self.request.community)
            .exclude_deleted()
            .select_related(
                "owner", "community", "parent", "parent__owner", "parent__community",
            )
            .prefetch_related("content_object")
            .order_by("created")
        )

    def get_comments_page(self, comments):
        return self.paginator_class(
            object_list=comments,
            count=self.object.num_comments or 0,
            per_page=self.paginate_by,
            allow_empty_first_page=True,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))
