# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models import Q
from django.template.response import TemplateResponse

from taggit.models import Tag

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.views import ParentObjectMixin


class TagDetailView(ParentObjectMixin, BaseActivityStreamView):
    template_name = "hashtags/tag_detail.html"
    ordering = "-created"

    parent_model = Tag
    parent_object_name = "tag"
    parent_required = False

    def get(self, request, *args, **kwargs):
        if self.tag is None:
            return TemplateResponse(
                request, "hashtags/not_found.html", {"tag": kwargs["slug"]}, status=404
            )
        return super().get(request, *args, **kwargs)

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


tag_detail_view = TagDetailView.as_view()
