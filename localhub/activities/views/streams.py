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


from localhub.common.views import BaseMultipleQuerySetListView, SearchMixin
from localhub.communities.views import CommunityRequiredMixin
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.polls.models import Poll
from localhub.posts.models import Post


class BaseStreamView(CommunityRequiredMixin, BaseMultipleQuerySetListView):
    ordering = "-created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models = [Photo, Post, Event, Poll]

    def filter_queryset(self, queryset):
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model):
        return self.filter_queryset(
            model.objects.for_activity_stream(self.request.user, self.request.community)
        )

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects)

    def get_querysets(self):
        return [self.get_queryset_for_model(model) for model in self.models]

    def get_count_querysets(self):
        return [self.get_count_queryset_for_model(model) for model in self.models]


class StreamView(BaseStreamView):
    template_name = "activities/stream.html"

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .following(self.request.user)
            .without_blocked(self.request.user)
        )


stream_view = StreamView.as_view()


class TimelineView(YearMixin, MonthMixin, DateMixin, StreamView):
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
    def sort_by_ascending(self):
        return self.request.GET.get("order") == "asc"

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
        return {"created__gte": since, "created__lt": until}

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
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
        return "created" if self.sort_by_ascending else "-created"

    def get_dates(self):
        """
        Calling dates() on a UNION queryset just returns list of PKs
        (Django bug?) so we need to build this separately for each
        queryset.
        """
        querysets = [
            qs.only("id", "created").select_related(None).dates("created", "month")
            for qs in self.get_queryset_dict().values()
        ]
        return sorted(set(itertools.chain.from_iterable(querysets)))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        for object in data["object_list"]:
            object["month"] = date_format(object["created"], "F Y")
        dates = self.get_dates()
        data.update(
            {
                "current_year": self.current_year,
                "months": self.get_months(dates),
                "years": self.get_years(dates),
                "date_filters": self.date_kwargs,
            }
        )
        return data


timeline_view = TimelineView.as_view()


class SearchView(SearchMixin, BaseStreamView):
    template_name = "activities/search.html"

    def get_ordering(self):
        return ("-rank", "-created") if self.search_query else None

    def filter_queryset(self, queryset):
        if self.search_query:
            return (
                super()
                .filter_queryset(queryset)
                .without_blocked(self.request.user)
                .search(self.search_query)
            )
        return queryset.none()


search_view = SearchView.as_view()
