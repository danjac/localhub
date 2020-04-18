# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.views.generic import ListView

from localhub.views import SearchMixin

from .mixins import ActivityQuerySetMixin, ActivityTemplateMixin


class BaseActivityListView(ActivityQuerySetMixin, ActivityTemplateMixin, ListView):
    allow_empty = True
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE


class ActivityListView(SearchMixin, BaseActivityListView):
    ordering = "-published"

    def get_ordering(self):
        if isinstance(self.ordering, str):
            ordering = [self.ordering]
        else:
            ordering = list(self.ordering)

        if self.search_query:
            ordering = ["-rank"] + ordering

        return ordering

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .published()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked(self.request.user)
        )

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs.order_by(*self.get_ordering())
