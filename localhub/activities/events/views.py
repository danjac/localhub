# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import calendar
import datetime

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
import pytz
from dateutil import relativedelta
from turbo_response import TurboFrame

# Localhub
from localhub.activities.views.generic import (
    activity_detail_view,
    activity_update_view,
    get_activity_queryset,
    handle_activity_create,
    render_activity_list,
)
from localhub.common.decorators import add_messages_to_response_header
from localhub.communities.decorators import community_required
from localhub.users.utils import has_perm_or_403

# Local
from .decorators import override_timezone
from .models import Event


@login_required
@community_required
@add_messages_to_response_header
@require_POST
def event_cancel_view(request, pk):
    event = get_object_or_404(get_activity_queryset(request, Event), pk=pk)
    has_perm_or_403(request.user, "events.cancel", event)

    event.canceled = timezone.now()
    event.save()
    event.notify_on_cancel(request.user)

    messages.success(request, _("This event has been canceled"))

    return redirect(event)


@login_required
@community_required
@add_messages_to_response_header
@require_POST
def event_attend_view(request, pk, remove=False):

    event = get_object_or_404(get_activity_queryset(request, Event), pk=pk)
    has_perm_or_403(request.user, "events.attend", event)

    if remove:
        event.attendees.remove(request.user)
        messages.info(request, _("You are no longer attending this event"))
    else:
        event.attendees.add(request.user)
        event.notify_on_attend(request.user)
        messages.success(request, _("You are now attending this event"))

    return (
        TurboFrame(event.get_dom_id() + "-attend")
        .template(
            "events/includes/attend.html",
            {"object": event, "is_attending": not (remove)},
        )
        .response(request)
    )


@community_required
@override_timezone
def event_download_view(request, pk):
    event = get_object_or_404(get_activity_queryset(request, Event), pk=pk)
    response = HttpResponse(content_type="text/calendar")
    response.write(event.to_ical())
    return response


@login_required
@community_required
@override_timezone
def event_create_view(request, model, form_class, **kwargs):

    has_perm_or_403(request.user, "activities.create_activity", request.community)

    try:
        [day, month, year] = [
            int(request.GET[param]) for param in ("day", "month", "year")
        ]
        starts = datetime.datetime(day=day, month=month, year=year, hour=9)
    except (KeyError, ValueError):
        starts = None

    initial = {"timezone": request.user.default_timezone, "starts": starts}

    return handle_activity_create(request, model, form_class, initial=initial, **kwargs)


event_update_view = override_timezone(activity_update_view)


event_detail_view = override_timezone(activity_detail_view)


@community_required
@override_timezone
def event_list_view(request, model, template_name):
    qs = (
        get_activity_queryset(request, model, with_common_annotations=True)
        .with_relevance()
        .with_timedelta()
    )
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
            datetime.datetime(
                day=day,
                month=month,
                year=year,
                tzinfo=pytz.UTC,
            )
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
