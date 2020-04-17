# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import calendar
import datetime

from django.http import Http404, HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic.dates import DateMixin, DayMixin, MonthMixin, YearMixin
from vanilla import GenericModelView

from localhub.activities.views.actions import BaseActivityActionView
from localhub.activities.views.form import ActivityCreateView
from localhub.activities.views.list import ActivityListView
from localhub.activities.views.mixins import ActivityQuerySetMixin

from .models import Event


class EventCreateView(ActivityCreateView):
    def get_form(self, data=None, files=None):
        form = super().get_form(data, files)
        form.initial["timezone"] = self.request.user.default_timezone
        return form


class EventListView(ActivityListView):
    ordering = ("-starts", "-published")


class EventCalendarView(YearMixin, MonthMixin, DayMixin, DateMixin, EventListView):
    template_name = "events/calendar.html"
    date_field = "starts"
    paginate_by = None
    allow_future = True
    model = Event

    def get_allow_empty(self):
        # mixin requirement
        return True

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
        qs = (
            super()
            .get_queryset()
            .filter(starts__month=self.current_month, starts__year=self.current_year)
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
            try:
                data["current_date"] = current_month = datetime.date(
                    day=self.current_day,
                    month=self.current_month,
                    year=self.current_year,
                )
            except ValueError:
                raise Http404
        data["current_month_days"] = days = self.get_days(current_month)
        data["today"] = now = timezone.now()
        data["is_today"] = (
            now.month == current_month.month and now.year == current_month.year
        )
        data["next_month"] = self.get_next_month(current_month)
        data["previous_month"] = self.get_previous_month(current_month)
        data["events"] = self.get_events(days)

        return data

    def get_events(self, days):
        """Group events by day
        """
        return {
            day: [e for e in self.object_list if e.starts.day == day] for day in days
        }

    def get_days(self, date):
        return list(calendar.Calendar().itermonthdays(date.year, date.month))


event_calendar_view = EventCalendarView.as_view()


class EventCancelView(BaseActivityActionView):
    success_message = _("This event has been canceled")
    permission_required = "events.cancel"
    model = Event

    def post(self, request, *args, **kwargs):
        self.object.canceled = timezone.now()
        self.object.save()
        self.object.notify_on_cancel(self.request.user)
        return self.success_response()


event_cancel_view = EventCancelView.as_view()


class BaseEventAttendView(BaseActivityActionView):
    permission_required = "events.attend"
    is_success_ajax_response = True
    model = Event


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


class EventDownloadView(ActivityQuerySetMixin, GenericModelView):
    """
    Generates a calendar .ics file.
    """

    model = Event

    def get(self, request, *args, **kwargs):
        self.object: Event = self.get_object()

        response = HttpResponse(content_type="text/calendar")
        response.write(self.object.to_ical())
        return response


event_download_view = EventDownloadView.as_view()
