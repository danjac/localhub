# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime
import itertools

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic.dates import _date_from_string

# Third Party Libraries
from dateutil import relativedelta

# Localhub
from localhub.common.pagination import PresetCountPaginator
from localhub.communities.decorators import community_required
from localhub.join_requests.models import JoinRequest
from localhub.notifications.models import Notification

# Local
from ..utils import get_activity_queryset_count, get_activity_querysets, load_objects


@community_required
def activity_stream_view(request):
    """
    Default "Home Page" of community.
    """
    qs_filter = (
        lambda qs: qs.published()
        .with_activity_stream_filters(request.user)
        .exclude_blocked(request.user)
    )

    context = {}

    if request.user.is_authenticated:
        context["notifications"] = (
            Notification.objects.for_community(request.community)
            .for_recipient(request.user)
            .exclude_blocked_actors(request.user)
            .unread()
            .select_related("actor", "content_type", "community", "recipient")
            .order_by("-created")
        )

    if request.user.has_perm("communities.manage_community", request.community):
        context["has_join_request"] = JoinRequest.objects.filter(
            sender=request.user,
            community=request.community,
            status__in=(JoinRequest.Status.PENDING, JoinRequest.Status.REJECTED),
        ).exists()

    return render_activity_stream(
        request,
        qs_filter,
        "activities/stream.html",
        ordering="-published",
        extra_context=context,
    )


@community_required
def activity_search_view(request):
    def _filter_queryset(qs):
        if request.search:
            return (
                qs.exclude_blocked(request.user)
                .published_or_owner(request.user)
                .search(request.search)
            )
        return qs.none()

    return render_activity_stream(
        request,
        _filter_queryset,
        "activities/search.html",
        ordering=("-rank", "-created") if request.search else None,
        extra_context={"non_search_path": reverse("activity_stream")},
    )


@community_required
def timeline_view(request):

    current_year, current_month = None, None

    try:
        current_year = _date_from_string(year=request.GET["year"], year_format="%Y")
    except (KeyError, Http404):
        pass

    if current_year:
        try:
            current_month = _date_from_string(
                year=current_year.year,
                year_format="%Y",
                month=request.GET["month"],
                month_format="%m",
            )
        except (KeyError, Http404):
            pass

    since, until = None, None

    if current_month:
        since = make_date_lookup_value(current_month)
        until = make_date_lookup_value(
            current_month + relativedelta.relativedelta(months=1)
        )
    elif current_year:
        since = make_date_lookup_value(current_year)
        until = make_date_lookup_value(
            current_year + relativedelta.relativedelta(years=1)
        )

    date_kwargs = (
        {"published__gte": since, "published__lt": until} if since and until else None
    )

    def _filter_queryset(qs, with_date_kwargs=True):
        qs = qs.published().exclude_blocked(request.user)
        if with_date_kwargs and date_kwargs:
            return qs.filter(**date_kwargs)
        return qs

    _, querysets = get_activity_querysets(
        lambda model: _filter_queryset(
            model.objects.for_activity_stream(
                request.user, request.community
            ).distinct(),
            with_date_kwargs=False,
        )
    )

    querysets = [
        qs.only("pk", "published").select_related(None).dates("published", "month")
        for qs in querysets
    ]

    dates = sorted(set(itertools.chain.from_iterable(querysets)))

    sort_order = request.GET.get("order", "desc")

    params = request.GET.copy()
    params["order"] = "desc" if sort_order == "asc" else "asc"
    if "page" in params:
        params.pop("page")
    reverse_sort_url = f"{request.path}?{params.urlencode()}"

    selected_dates = dates

    if current_year:
        selected_dates = [date for date in dates if date.year == current_year.year]

    if current_month:
        selected_dates = [
            date for date in selected_dates if date.month == current_month.month
        ]

    response = render_activity_stream(
        request,
        _filter_queryset,
        "activities/timeline.html",
        ordering="published" if sort_order == "asc" else "-published",
        page_size=settings.LONG_PAGE_SIZE,
        extra_context={
            "current_month": current_month.month if current_month else None,
            "current_year": current_year.year if current_year else None,
            "date_filters": date_kwargs,
            "dates": dates,
            "months": get_months(dates),
            "order": sort_order,
            "reverse_sort_url": reverse_sort_url,
            "selected_dates": selected_dates,
            "selected_months": get_months(selected_dates),
            "selected_years": get_years(selected_dates),
            "years": get_years(dates),
        },
    )

    for obj in response.context_data["object_list"]:
        obj["month"] = date_format(obj["published"], "F Y")
    return response


@community_required
@login_required
def private_view(request):
    def _filter_queryset(qs):
        qs = qs.private(request.user)
        if request.search:
            qs = qs.search(request.search)
        return qs

    return render_activity_stream(
        request,
        _filter_queryset,
        "activities/private.html",
        ordering=("-rank", "-created") if request.search else "-created",
    )


def render_activity_stream(
    request,
    queryset_filter,
    template_name,
    *,
    ordering=("-created", "-published"),
    page_size=settings.DEFAULT_PAGE_SIZE,
    extra_context=None,
):
    """
    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """

    qs, querysets = get_activity_querysets(
        lambda model: queryset_filter(
            model.objects.for_community(request.community)
            .for_activity_stream(request.user, request.community)
            .distinct()
        ),
        ordering=ordering,
    )

    count = get_activity_queryset_count(
        lambda model: queryset_filter(
            model.objects.for_community(request.community).distinct()
        )
    )

    page = PresetCountPaginator(
        object_list=qs, count=count, per_page=page_size, allow_empty_first_page=True,
    ).get_page(request.GET.get("q", 1))

    page = load_objects(page, querysets)
    print(extra_context)

    context = {
        "page_obj": page,
        "paginator": page.paginator,
        "object_list": page.object_list,
        "is_paginated": page.has_other_pages(),
        **(extra_context or {}),
    }

    return TemplateResponse(request, template_name, context)


def get_months(dates, year=None):
    return [
        (date.strftime("%-m"), date.strftime("%B"))
        for date in dates
        if year is None or date.year == year
    ]


def get_years(dates):
    return sorted(set([date.year for date in dates]))


def make_date_lookup_value(value):
    value = datetime.datetime.combine(value, datetime.time.min)
    if settings.USE_TZ:
        value = timezone.make_aware(value)
    return value
