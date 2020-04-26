# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic.dates import DateMixin, DayMixin, MonthMixin, YearMixin

import pytz

from localhub.activities.views.list_detail import ActivityListView, BaseActivityListView

from ..models import Event


class EventListView(ActivityListView):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_relevance()
            .with_timedelta()
            .order_by("-relevance", "timedelta")
        )


class EventCalendarView(
    YearMixin, MonthMixin, DayMixin, DateMixin, BaseActivityListView
):
    template_name = "events/calendar.html"
    date_field = "starts"
    paginate_by = None
    allow_future = True
    model = Event

    def get_allow_empty(self):
        return not (self.current_day)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except ValueError:
            raise Http404("These dates are not valid")

    @cached_property
    def current_day(self):
        try:
            return int(self.get_day())
        except (Http404, ValueError):
            return None

    @cached_property
    def current_month(self):
        try:
            return int(self.get_month())
        except (Http404, ValueError):
            return timezone.now().month

    @cached_property
    def current_year(self):
        try:
            return int(self.get_year())
        except (Http404, ValueError):
            return timezone.now().year

    def get_queryset(self):
        # for rep
        qs = (
            super()
            .get_queryset()
            .published_or_owner(self.request.user)
            .with_next_date()
            .exclude_blocked(self.request.user)
            .filter(parent__isnull=True,)
            .order_by("next_date")
        )
        if self.current_day:
            qs = qs.for_date(self.current_day, self.current_month, self.current_year)
        else:
            qs = qs.for_month(self.current_month, self.current_year)
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["current_month"] = current_month = datetime.date(
            day=1, month=self.current_month, year=self.current_year,
        )

        if self.current_day:
            # we don't need all the complicated calendar data,
            # just events for this day
            data["current_date"] = current_month = datetime.date(
                day=self.current_day, month=self.current_month, year=self.current_year,
            )
            data["events"] = [
                e
                for e in self.object_list
                if e.matches_date(
                    datetime.datetime(
                        day=self.current_day,
                        month=self.current_month,
                        year=self.current_year,
                        tzinfo=pytz.UTC,
                    )
                )
            ]
            return data

        now = timezone.now()

        data.update(
            {
                "next_month": self.get_next_month(current_month),
                "previous_month": self.get_previous_month(current_month),
                "slots": self.get_slots(current_month),
                "today": now,
                "is_today": now.month == current_month.month
                and now.year == current_month.year,
            }
        )

        return data

    def get_slots(self, date):
        """Group events by day into tuples of (number, events)
        """

        return [
            (day, [e for e in self.object_list if dt and e.matches_date(dt)])
            for day, dt in self.iter_dates(date)
        ]

    def iter_dates(self, date):
        """Yields tuple of (counter, datetime) for each day of month. If day
        falls out of range yields zero, None.
        """
        for day in calendar.Calendar().itermonthdays(date.year, date.month):
            if day > 0:
                yield day, datetime.datetime(
                    day=day, month=date.month, year=date.year, tzinfo=pytz.UTC
                )
            else:
                # falls outside the day range
                yield 0, None


event_calendar_view = EventCalendarView.as_view()
