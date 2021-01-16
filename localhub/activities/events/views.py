# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import calendar
import datetime

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

# Third Party Libraries
import pytz
from dateutil import relativedelta
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TurboFrame

# Localhub
from localhub.activities.views.generic import (
    ActivityQuerySetMixin,
    BaseActivityActionView,
    activity_detail_view,
    activity_update_view,
    get_activity_queryset,
    handle_activity_create,
    render_activity_list,
)
from localhub.communities.decorators import community_required
from localhub.users.utils import has_perm_or_403

# Local
from .decorators import override_timezone
from .mixins import TimezoneOverrideMixin
from .models import Event


class BaseEventActionView(BaseActivityActionView):

    model = Event


class EventCancelView(PermissionRequiredMixin, BaseEventActionView):
    success_message = _("This event has been canceled")

    permission_required = "events.cancel"

    def post(self, request, *args, **kwargs):
        self.object.canceled = timezone.now()
        self.object.save()
        self.object.notify_on_cancel(self.request.user)
        messages.success(request, self.success_message)

        return self.render_to_response()


event_cancel_view = EventCancelView.as_view()


class BaseEventAttendView(PermissionRequiredMixin, BaseEventActionView):
    permission_required = "events.attend"

    def render_to_response(self, is_attending):
        return (
            TurboFrame(self.object.get_dom_id() + "-attend")
            .template(
                "events/includes/attend.html",
                {"object": self.object, "is_attending": is_attending},
            )
            .response(self.request)
        )


class EventAttendView(BaseEventAttendView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.add(self.request.user)
        self.object.notify_on_attend(self.request.user)
        return self.render_to_response(is_attending=True)


event_attend_view = EventAttendView.as_view()


class EventUnattendView(BaseEventAttendView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.remove(self.request.user)
        return self.render_to_response(is_attending=False)


event_unattend_view = EventUnattendView.as_view()


class EventDownloadView(
    ActivityQuerySetMixin, SingleObjectMixin, TimezoneOverrideMixin, View
):
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


@community_required
@login_required
@override_timezone
def event_create_view(request, model, form_class, **kwargs):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    if request.method == "POST":
        form = form_class(request.POST)
    else:
        try:
            [day, month, year] = [
                int(request.GET[param]) for param in ("day", "month", "year")
            ]
            starts = datetime.datetime(day=day, month=month, year=year, hour=9)
        except (KeyError, ValueError):
            starts = None

        form = form_class(
            initial={"timezone": request.user.default_timezone, "starts": starts}
        )

    return handle_activity_create(request, model, form, **kwargs)


event_update_view = override_timezone(activity_update_view)


event_detail_view = override_timezone(activity_detail_view)


@community_required
@override_timezone
def event_list_view(request, model, template_name):
    qs = get_activity_queryset(request, model).with_relevance().with_timedelta()
    return render_activity_list(
        request, qs, template_name, ordering=("-relevance", "timedelta")
    )


@community_required
@override_timezone
def event_calendar_view(request):

    now = timezone.localtime(timezone.now())

    def _get_date_value(param, default):
        try:
            return int(request.GET[param])
        except (KeyError, ValueError):
            return default

    day, month, year = [
        _get_date_value(param, default)
        for param, default in [("day", None), ("month", now.month), ("year", now.year)]
    ]

    try:
        qs = (
            Event.objects.for_community(request.community)
            .published_or_owner(request.user)
            .with_next_date()
            .exclude_blocked(request.user)
            .filter(parent__isnull=True)
            .order_by("next_date")
        )

        if day:
            qs = qs.for_date(day, month, year).with_common_annotations(
                request.user, request.community
            )
        else:
            qs = qs.for_month(month, year)
    except Event.InvalidDate:
        raise Http404("Invalid date")

    context = {}

    if day:
        match_datetime = make_datetime(day, month, year)

        context = {
            "current_date": make_date(day, month, year),
            "events": [event for event in qs if event.matches_date(match_datetime)],
        }

    else:
        first_of_month = make_date(1, month, year)
        context = {
            "events": qs,
            "current_month": first_of_month,
            "next_month": first_of_month + relativedelta.relativedelta(months=+1),
            "previous_month": first_of_month + relativedelta.relativedelta(months=-1),
            "today": now,
            "is_current_month": now.month == first_of_month.month
            and now.year == first_of_month.year,
            "slots": [
                (
                    day,
                    is_past,
                    [event for event in qs if dt and event.matches_date(dt)],
                )
                for day, is_past, dt in iter_dates(day, month, year)
            ],
        }
    return TemplateResponse(request, "events/calendar.html", context)


def make_datetime(day, month, year):
    try:
        return timezone.localtime(
            datetime.datetime(day=day, month=month, year=year, tzinfo=pytz.UTC,)
        )
    except ValueError:
        raise Http404("Invalid date")


def make_date(day, month, year):
    return make_datetime(day, month, year).date()


def is_past(day, month, year):
    now = timezone.now()
    # any month in the future
    if month > now.month and year >= now.year:
        return False

    # any month in the past
    if month < now.month:
        return True

    # this month
    return now.day > day


def iter_dates(day, month, year):
    """Yields tuple of (counter, is_past, datetime) for each day of month. If day
    falls out of range yields zero, False, None.
    """
    try:
        for day in calendar.Calendar().itermonthdays(year, month):
            if day > 0:
                yield day, is_past(day, month, year), make_datetime(day, month, year)
            else:
                # falls outside the day range
                yield 0, False, None
    except ValueError:
        raise Http404("Invalid date")
