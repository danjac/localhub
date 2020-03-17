# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import itertools

from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.functional import cached_property
from django.views.generic.dates import (
    DateMixin,
    MonthMixin,
    YearMixin,
    _date_from_string,
)
from vanilla import TemplateView

from localhub.communities.views import CommunityRequiredMixin
from localhub.notifications.models import Notification
from localhub.pagination import PresetCountPaginator
from localhub.views import SearchMixin

from ..models import get_activity_queryset_count, get_activity_querysets, load_objects


class BaseActivityStreamView(CommunityRequiredMixin, TemplateView):
    """
    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """

    allow_empty = True
    ordering = ("-published", "-created")

    paginate_by = settings.DEFAULT_PAGE_SIZE
    paginator_class = PresetCountPaginator
    page_kwarg = "page"

    def get_ordering(self):
        return self.ordering

    def filter_queryset(self, queryset):
        """
        Override this method for view-specific filtering
        """
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model):
        """
        Include any annotations etc you need
        """
        return model.objects.for_activity_stream(
            self.request.user, self.request.community
        )

    def get_count_queryset_for_model(self, model):
        """
        We do not usually need all the additional annotations etc for the count.
        """
        return model.objects

    def get_count(self):
        return get_activity_queryset_count(
            lambda model: self.filter_queryset(self.get_count_queryset_for_model(model))
        )

    def get_page(self):
        qs, querysets = get_activity_querysets(
            lambda model: self.filter_queryset(self.get_queryset_for_model(model)),
            ordering=self.get_ordering(),
        )

        page = self.paginator_class(
            object_list=qs,
            count=self.get_count(),
            per_page=self.paginate_by,
            allow_empty_first_page=self.allow_empty,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))

        return load_objects(page, querysets)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        page = self.get_page()
        data.update(
            {
                "page_obj": page,
                "paginator": page.paginator,
                "object_list": page.object_list,
                "is_paginated": page.has_other_pages(),
            }
        )
        return data


class ActivityStreamView(BaseActivityStreamView):
    """
    Default "Home Page" of community.
    """

    template_name = "activities/stream.html"

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .with_activity_stream_filters(self.request.user)
            .exclude_blocked(self.request.user)
        )

    def get_latest_notification(self):
        return (
            Notification.objects.for_community(self.request.community)
            .for_recipient(self.request.user)
            .exclude_blocked_actors(self.request.user)
            .unread()
            .select_related("actor", "content_type")
            .order_by("-created")
            .first()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({"latest_notification": self.get_latest_notification()})
        return data


activity_stream_view = ActivityStreamView.as_view()


class ActivitySearchView(SearchMixin, BaseActivityStreamView):
    template_name = "activities/search.html"
    search_optional = False

    def get_ordering(self):
        return ("-rank", "-published") if self.search_query else None

    def filter_queryset(self, queryset):
        if self.search_query:
            return (
                super()
                .filter_queryset(queryset)
                .exclude_blocked(self.request.user)
                .published()
                .search(self.search_query)
            )
        return queryset.none()


activity_search_view = ActivitySearchView.as_view()


class TimelineView(YearMixin, MonthMixin, DateMixin, BaseActivityStreamView):
    template_name = "activities/timeline.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE * 2
    month_format = "%B"

    @property
    def uses_datetime_field(self):
        """
        Always return True, as we're using an explicit field not
        specific to a single model.
        """
        return True

    @cached_property
    def sort_order(self):
        return self.request.GET.get("order", "desc")

    @cached_property
    def sort_by_ascending(self):
        return self.sort_order == "asc"

    @cached_property
    def current_year(self):
        return (self.get_current_year() or timezone.now()).year

    @cached_property
    def date_kwargs(self):
        date = self.get_current_month()
        if date:
            return self.make_date_lookup_kwargs(
                self._make_date_lookup_arg(date),
                self._make_date_lookup_arg(self._get_next_month(date)),
            )

        date = self.get_current_year()
        if date:
            return self.make_date_lookup_kwargs(
                self._make_date_lookup_arg(date),
                self._make_date_lookup_arg(self._get_next_year(date)),
            )

        return None

    def get_current_year(self):
        try:
            return _date_from_string(
                year=self.get_year(), year_format=self.get_year_format()
            )
        except Http404:
            return None

    def get_current_month(self):
        try:
            return _date_from_string(
                year=self.get_year(),
                year_format=self.get_year_format(),
                month=self.get_month(),
                month_format="%m",
            )
        except Http404:
            return None

    def make_date_lookup_kwargs(self, since, until):
        return {"published__gte": since, "published__lt": until}

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .published()
            .exclude_blocked(self.request.user)
        )
        if self.date_kwargs:
            return qs.filter(**self.date_kwargs)
        return qs

    def get_months(self, dates):
        """
        Get months for *current* year as list of tuples of (order, name)
        """
        return [
            (date.strftime("%-m"), date.strftime(self.get_month_format()))
            for date in dates
            if date.year == self.current_year
        ]

    def get_years(self, dates):
        """
        Return list of years in numerical format.
        """
        return sorted(set([date.year for date in dates]))

    def get_ordering(self):
        return "published" if self.sort_by_ascending else "-published"

    def get_dates(self):
        """
        Calling dates() on a UNION queryset just returns list of PKs
        (Django bug?) so we need to build this separately for each
        queryset.
        """
        _, querysets = get_activity_querysets(
            lambda model: self.filter_queryset(self.get_queryset_for_model(model))
        )
        querysets = [
            qs.only("pk", "published").select_related(None).dates("published", "month")
            for qs in querysets
        ]
        return sorted(set(itertools.chain.from_iterable(querysets)))

    def get_reverse_sort_url(self):
        """
        Get all params and switch out the current order.
        """
        params = self.request.GET.copy()
        params["order"] = "desc" if self.sort_by_ascending else "asc"
        return f"{self.request.path}?{params.urlencode()}"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        for object in data["object_list"]:
            object["month"] = date_format(object["published"], "F Y")
        dates = self.get_dates()
        data.update(
            {
                "dates": dates,
                "current_year": self.current_year,
                "reverse_sort_url": self.get_reverse_sort_url(),
                "months": self.get_months(dates),
                "years": self.get_years(dates),
                "order": self.sort_order,
                "date_filters": self.date_kwargs,
            }
        )
        return data


timeline_view = TimelineView.as_view()


class DraftsView(BaseActivityStreamView):
    """
    Shows draft posts belonging to this user.
    """

    ordering = "-created"
    template_name = "activities/drafts.html"

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).drafts(self.request.user)


drafts_view = DraftsView.as_view()
