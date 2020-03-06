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

from localhub.communities.views import CommunityRequiredMixin
from localhub.notifications.models import Notification
from localhub.private_messages.models import Message
from localhub.views import BaseMultipleQuerySetListView, SearchMixin

from ..models import get_activity_models


class BaseStreamView(CommunityRequiredMixin, BaseMultipleQuerySetListView):

    allow_empty = True
    ordering = ("-published", "-created")
    paginate_by = settings.DEFAULT_PAGE_SIZE

    @cached_property
    def models(self):
        return get_activity_models()

    def filter_queryset(self, queryset):
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model):
        return self.filter_queryset(
            model.objects.for_activity_stream(self.request.user, self.request.community)
        )

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects)

    def get_querysets(self):
        # get_activity_models
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
            .published()
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

    def get_latest_message(self):
        return (
            Message.objects.for_community(self.request.community)
            .for_recipient(self.request.user)
            .exclude_blocked(self.request.user)
            .unread()
            .select_related(
                "sender", "recipient", "thread", "thread__sender", "thread__recipient"
            )
            .order_by("-created")
            .first()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        message = self.get_latest_message()
        message_url = message.resolve_url(self.request.user) if message else None

        data.update(
            {
                "latest_notification": self.get_latest_notification(),
                "latest_message": message,
                "latest_message_url": message_url,
            }
        )
        return data


stream_view = StreamView.as_view()


class TimelineView(YearMixin, MonthMixin, DateMixin, BaseStreamView):
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
        querysets = [
            qs.only("id", "published").select_related(None).dates("published", "month")
            for qs in self.get_queryset_dict().values()
        ]
        return sorted(set(itertools.chain.from_iterable(querysets)))

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        for object in data["object_list"]:
            object["month"] = date_format(object["published"], "F Y")
        dates = self.get_dates()
        data.update(
            {
                "dates": dates,
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


search_view = SearchView.as_view()


class DraftsView(BaseStreamView):
    """
    Shows draft posts belonging to this user.
    """

    ordering = "-created"
    template_name = "activities/drafts.html"

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).drafts(self.request.user)


drafts_view = DraftsView.as_view()
