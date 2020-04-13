# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from taggit.models import Tag

from localhub.activities.views.streams import BaseActivityStreamView


class TagDetailView(BaseActivityStreamView):
    template_name = "hashtags/tag_detail.html"
    ordering = "-created"

    @cached_property
    def tag(self):
        return get_object_or_404(Tag, slug=self.kwargs["slug"])

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .exclude_blocked_users(self.request.user)
            .published_or_owner(self.request.user)
            .filter(tags__name__in=[self.tag.name])
            .distinct()
        )

        # ensure we block all unwanted tags *unless* it's the tag
        # in question.
        if self.request.user.is_authenticated:
            qs = qs.exclude(
                Q(tags__in=self.request.user.blocked_tags.exclude(id=self.tag.id)),
                ~Q(owner=self.request.user),
            )
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tag"] = self.tag
        return data


tag_detail_view = TagDetailView.as_view()
