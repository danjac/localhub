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
from django.views.generic import TemplateView
from django.views.generic.dates import _date_from_string

# Third Party Libraries
from dateutil import relativedelta

# Localhub
from localhub.common.pagination import PresetCountPaginator
from localhub.communities.decorators import community_required
from localhub.communities.mixins import CommunityRequiredMixin
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
        lambda qs: qs.for_community(request.community)
        .published()
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
    search = request.GET.get("q", None)

    def _filter_queryset(qs):
        if search:
            return (
                qs.for_community(request.community)
                .exclude_blocked(request.user)
                .published_or_owner(request.user)
                .search(search)
            )
        return qs.none()

    return render_activity_stream(
        request,
        _filter_queryset,
        "activities/search.html",
        ordering=("-rank", "-created") if search else None,
        extra_context={"search": search, "non_search_path": reverse("activity_stream")},
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
        qs = (
            qs.for_community(request.community)
            .published()
            .exclude_blocked(request.user)
        )
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

    sort_order = request.GET.get("order", "desc")

    dates = sorted(set(itertools.chain.from_iterable(querysets)))

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
    search = request.GET.get("q", None)

    def _filter_queryset(qs):
        qs = qs.for_community(request.community).private(request.user)
        if search:
            qs = qs.search(search)
        return qs

    return render_activity_stream(
        request,
        _filter_queryset,
        "activities/private.html",
        ordering=("-rank", "-created") if search else "-created",
        extra_context={"search": search},
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
            model.objects.for_activity_stream(
                request.user, request.community
            ).distinct()
        ),
        ordering=ordering,
    )

    count = get_activity_queryset_count(
        lambda model: queryset_filter(model.objects.distinct())
    )

    page = PresetCountPaginator(
        object_list=qs, count=count, per_page=page_size, allow_empty_first_page=True,
    ).get_page(request.GET.get("q", 1))

    page = load_objects(page, querysets)

    context = {
        "page_obj": page,
        "paginator": page.paginator,
        "object_list": page.object_list,
        "is_paginated": page.has_other_pages(),
        **(extra_context or None),
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


class BaseActivityStreamView(CommunityRequiredMixin, TemplateView):
    """
    Pattern adapted from:
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    """

    allow_empty = True
    ordering = ("-created", "-published")

    paginate_by = settings.DEFAULT_PAGE_SIZE
    paginator_class = PresetCountPaginator
    page_kwarg = "page"

    def get_ordering(self):
        return self.ordering

    def filter_queryset(self, queryset):
        """
        Override this method for view-specific filtering
        """
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model):
        """
        Include any annotations etc you need
        """
        return model.objects.for_activity_stream(
            self.request.user, self.request.community
        ).distinct()

    def get_count_queryset_for_model(self, model):
        """
        We do not usually need all the additional annotations etc for the count.
        """
        return model.objects.distinct()

    def get_count(self):
        return get_activity_queryset_count(
            lambda model: self.filter_queryset(self.get_count_queryset_for_model(model))
        )

    def get_page(self):
        qs, querysets = get_activity_querysets(
            lambda model: self.filter_queryset(self.get_queryset_for_model(model)),
            ordering=self.get_ordering(),
        )

        page = self.paginator_class(
            object_list=qs,
            count=self.get_count(),
            per_page=self.paginate_by,
            allow_empty_first_page=self.allow_empty,
        ).get_page(self.request.GET.get(self.page_kwarg, 1))

        return load_objects(page, querysets)

    def get_context_data(self, **kwargs):
        page = self.get_page()
        return {
            **super().get_context_data(**kwargs),
            **{
                "page_obj": page,
                "paginator": page.paginator,
                "object_list": page.object_list,
                "is_paginated": page.has_other_pages(),
            },
        }
