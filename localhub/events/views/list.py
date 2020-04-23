# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic.dates import DateMixin, DayMixin, MonthMixin, YearMixin

from localhub.activities.views.list import ActivityListView, BaseActivityListView

from .models import Event


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
            .exclude_blocked(self.request.user)
            .filter(
                parent__isnull=True,
                starts__month=self.current_month,
                starts__year=self.current_year,
            )
            .order_by("starts")
        )
        if self.current_day:
            qs = qs.filter(starts__day=self.current_day)
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # TBD: error handling, raise 404 if borked
        try:
            data["current_month"] = current_month = datetime.date(
                day=1, month=self.current_month, year=self.current_year,
            )
        except ValueError:
            raise Http404

        if self.current_day:
            # we just need current date, nothing else
            try:
                data["current_date"] = current_month = datetime.date(
                    day=self.current_day,
                    month=self.current_month,
                    year=self.current_year,
                )
            except ValueError:
                raise Http404
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
            (day, [e for e in self.object_list if e.starts.day == day])
            for day in calendar.Calendar().itermonthdays(date.year, date.month)
        ]


event_calendar_view = EventCalendarView.as_view()
