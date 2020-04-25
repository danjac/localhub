# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic.dates import DateMixin, DayMixin, MonthMixin, YearMixin

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
        # simplified queryset: we don't need likes etc.
        # order by starts with earliest first, so they
        # appear in the right order in day views/slots.
        qs = (
            super()
            .get_queryset()
            .published()
            .with_next_date(self.current_date)
            .exclude_blocked(self.request.user)
            .filter(
                parent__isnull=True,
                next_date__month=self.current_month,
                next_date__year=self.current_year,
            )
            .order_by("next_date")
        )
        if self.current_day:
            qs = qs.filter(next_date__day=self.current_day)
        return qs

    @cached_property
    def first_of_month(self):
        """Returns 1st of the month specified in URL (or today)
        """
        try:
            return datetime.date(
                day=1, month=self.current_month, year=self.current_year,
            )
        except ValueError:
            raise Http404

    @cached_property
    def current_date(self):
        """
        Returns the current date if specified, otherwise
        returns None.
        """
        if not self.current_day:
            return self.first_of_month
        try:
            return datetime.date(
                day=self.current_day, month=self.current_month, year=self.current_year,
            )
        except ValueError:
            raise Http404

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["current_month"] = self.current_date

        if self.current_day:
            data["current_date"] = self.current_date

        now = timezone.now()

        data.update(
            {
                "next_month": self.get_next_month(self.current_date),
                "previous_month": self.get_previous_month(self.current_date),
                "slots": self.get_slots(self.current_date),
                "today": now,
                "is_today": now.month == self.current_date.month
                and now.year == self.current_date.year,
            }
        )

        return data

    def get_slots(self, date):
        """Group events by day into tuples of (number, events)
        """
        return [
            (day, [e for e in self.object_list if e.starts.day == day])
            for day in calendar.Calendar().itermonthdays(date.year, date.month)
        ]


event_calendar_view = EventCalendarView.as_view()
