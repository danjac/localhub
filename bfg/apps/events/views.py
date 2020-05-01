# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.http import Http404, HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.dates import DateMixin, DayMixin, MonthMixin, YearMixin
from django.views.generic.detail import SingleObjectMixin

import pytz

from bfg.apps.activities.views.generic import (
    ActivityCreateView,
    ActivityListView,
    ActivityQuerySetMixin,
    BaseActivityActionView,
    BaseActivityListView,
)

from .models import Event


class BaseEventActionView(BaseActivityActionView):

    model = Event


class EventCancelView(BaseEventActionView):
    success_message = _("This event has been canceled")

    permission_required = "events.cancel"

    def post(self, request, *args, **kwargs):
        self.object.canceled = timezone.now()
        self.object.save()
        self.object.notify_on_cancel(self.request.user)
        return self.success_response()


event_cancel_view = EventCancelView.as_view()


class BaseEventAttendView(BaseEventActionView):
    permission_required = "events.attend"
    is_success_ajax_response = True


class EventAttendView(BaseEventAttendView):
    success_message = _("You are now attending this event")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.add(self.request.user)
        self.object.notify_on_attend(self.request.user)
        return self.success_response()


event_attend_view = EventAttendView.as_view()


class EventUnattendView(BaseEventAttendView):
    success_message = _("You are no longer attending this event")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.remove(self.request.user)
        return self.success_response()


event_unattend_view = EventUnattendView.as_view()


class EventDownloadView(ActivityQuerySetMixin, SingleObjectMixin, View):
    """
    Generates a calendar .ics file.
    """

    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        response = HttpResponse(content_type="text/calendar")
        response.write(self.object.to_ical())
        return response


event_download_view = EventDownloadView.as_view()


class EventCreateView(ActivityCreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial["timezone"] = self.request.user.default_timezone
        return initial


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
        # empty month view is fine, but you should not be able
        # to navigate to a single date missing any events.
        return not (self.current_day)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Event.InvalidDate:
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
            .filter(parent__isnull=True)
            .order_by("next_date")
        )
        if self.current_day:
            qs = qs.for_date(self.current_day, self.current_month, self.current_year)
        else:
            qs = qs.for_month(self.current_month, self.current_year)
        return qs

    def make_date(self, day):
        try:
            return datetime.date(
                day=day, month=self.current_month, year=self.current_year,
            )
        except ValueError:
            raise Event.InvalidDate()

    def make_datetime(self, day):
        try:
            return datetime.datetime(
                day=day,
                month=self.current_month,
                year=self.current_year,
                tzinfo=pytz.UTC,
            )
        except ValueError:
            raise Event.InvalidDate()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if self.current_day:
            data["current_date"] = self.make_date(self.current_day)
            match_datetime = self.make_datetime(self.current_day)
            data["events"] = [
                event
                for event in self.object_list
                if event.matches_date(match_datetime)
            ]
            return data

        now = timezone.now()

        data["current_month"] = first_of_month = self.make_date(1)

        data.update(
            {
                "next_month": self.get_next_month(first_of_month),
                "previous_month": self.get_previous_month(first_of_month),
                "slots": self.get_slots(),
                "today": now,
                "is_today": now.month == first_of_month.month
                and now.year == first_of_month.year,
            }
        )

        return data

    def get_slots(self):
        """Group events by day into tuples of (number, events)
        """

        return [
            (
                day,
                is_past,
                [event for event in self.object_list if dt and event.matches_date(dt)],
            )
            for day, is_past, dt in self.iter_dates()
        ]

    def is_past(self, day):
        now = timezone.now()
        # any month in the future
        if self.current_month > now.month and self.current_year >= now.year:
            return False

        # any month in the past
        if self.current_month < now.month:
            return True

        # this month
        return now.day > day

    def iter_dates(self):
        """Yields tuple of (counter, is_past, datetime) for each day of month. If day
        falls out of range yields zero, False, None.
        """
        try:
            for day in calendar.Calendar().itermonthdays(
                self.current_year, self.current_month
            ):
                if day > 0:
                    yield day, self.is_past(day), self.make_datetime(day=day)
                else:
                    # falls outside the day range
                    yield 0, False, None
        except ValueError:
            raise Event.InvalidDate()


event_calendar_view = EventCalendarView.as_view()
