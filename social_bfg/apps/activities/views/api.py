# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import itertools

# Django
from django.conf import settings
from django.db import IntegrityError
from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic.dates import (
    DateMixin,
    MonthMixin,
    YearMixin,
    _date_from_string,
)

# Django Rest Framework
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

# Social-BFG
from social_bfg.apps.bookmarks.models import Bookmark
from social_bfg.apps.comments.serializers import CommentSerializer
from social_bfg.apps.communities.permissions import IsCommunityMember
from social_bfg.apps.events.models import Event
from social_bfg.apps.events.serializers import EventSerializer
from social_bfg.apps.likes.models import Like
from social_bfg.apps.photos.models import Photo
from social_bfg.apps.photos.serializers import PhotoSerializer
from social_bfg.apps.polls.models import Poll
from social_bfg.apps.polls.serializers import PollSerializer
from social_bfg.apps.posts.models import Post
from social_bfg.apps.posts.serializers import PostSerializer
from social_bfg.pagination import PresetCountPaginator

# Local
from ..permissions import IsActivityOwner, IsNotActivityOwner
from ..utils import get_activity_queryset_count, get_activity_querysets, load_objects

# For now parking all "API" views here. Will eventually remove existing views
# and split these up in to "generic" and "streams" modules as before. Also
# all other API views in other apps will follow same pattern.


class StreamPaginator(PageNumberPagination):

    page_size = settings.SOCIAL_BFG_DEFAULT_PAGE_SIZE

    def __init__(self, count):
        self.count = count

    def django_paginator_class(self, queryset, page_size):
        return PresetCountPaginator(self.count, queryset, page_size)


class BaseActivityStreamAPIView(APIView):
    """Provides a generic stream of different activities. Subclasses
    will always be paginated.
    """

    ordering = ("-published", "-created")

    permission_classes = [
        IsCommunityMember,
    ]

    pagination_class = StreamPaginator

    serializer_classes = {
        Post: PostSerializer,
        Event: EventSerializer,
        Poll: PollSerializer,
        Photo: PhotoSerializer,
    }

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

    def get_serializer_class(self, obj):
        return self.serializer_classes[obj.__class__]

    def get_serializer_context(self):
        return {
            "request": self.request,
            "format": self.format_kwarg,
            "view": self,
        }

    def get_serializer(self, obj):
        serializer_class = self.get_serializer_class(obj)
        return serializer_class(obj, context=self.get_serializer_context())

    @cached_property
    def paginator(self):
        """
        These views are always paginated, so no need to check.
        """
        return self.pagination_class(self.get_count())

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)

    def paginate_querysets(self):
        qs, querysets = get_activity_querysets(
            lambda model: self.filter_queryset(self.get_queryset_for_model(model)),
            ordering=self.get_ordering(),
        )
        object_list = self.paginator.paginate_queryset(qs, self.request, view=self)
        return load_objects(object_list, querysets)

    def get(self, request, *args, **kwargs):
        data = [
            self.get_serializer(item["object"]).data
            for item in self.paginate_querysets()
        ]
        return self.get_paginated_response(data)


class DefaultActivityStreamAPIView(BaseActivityStreamAPIView):
    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .with_activity_stream_filters(self.request.user)
            .exclude_blocked(self.request.user)
        )


default_activity_stream_api_view = DefaultActivityStreamAPIView.as_view()


class ActivitySearchAPIView(BaseActivityStreamAPIView):
    # will fold in SearchMixin later

    search_param = "q"

    @cached_property
    def search_query(self):
        return self.request.GET.get(self.search_param)

    def get_ordering(self):
        return ("-rank", "-created") if self.search_query else None

    def filter_queryset(self, queryset):
        if self.search_query:
            return (
                super()
                .filter_queryset(queryset)
                .exclude_blocked(self.request.user)
                .published_or_owner(self.request.user)
                .search(self.search_query)
            )
        return queryset.none()


activity_search_api_view = ActivitySearchAPIView.as_view()


class TimelineAPIView(YearMixin, MonthMixin, DateMixin, BaseActivityStreamAPIView):

    month_format = "%B"

    @property
    def uses_datetime_field(self):
        """
        Always return True, as we're using an explicit field not
        specific to a single model.
        """
        return True

    @cached_property
    def sort_order(self):
        return self.request.GET.get("order", "desc")

    @cached_property
    def sort_by_ascending(self):
        return self.sort_order == "asc"

    @cached_property
    def current_year(self):
        date = self.get_current_year()
        if date:
            return date.year
        return None

    @cached_property
    def current_month(self):
        date = self.get_current_month()
        if date:
            return date.month
        return None

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

    def filter_queryset(self, queryset, with_date_kwargs=True):
        qs = (
            super()
            .filter_queryset(queryset)
            .published()
            .exclude_blocked(self.request.user)
        )
        if with_date_kwargs and self.date_kwargs:
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
        _, querysets = get_activity_querysets(
            lambda model: self.filter_queryset(
                self.get_queryset_for_model(model), with_date_kwargs=False
            )
        )
        querysets = [
            qs.only("pk", "published").select_related(None).dates("published", "month")
            for qs in querysets
        ]
        return sorted(set(itertools.chain.from_iterable(querysets)))

    def get_reverse_sort_url(self):
        """
        Get all params and switch the current order parameter.
        """
        params = self.request.GET.copy()
        params["order"] = "desc" if self.sort_by_ascending else "asc"
        # reset pagination
        if "page" in params:
            params.pop("page")
        return f"{self.request.path}?{params.urlencode()}"

    def get_selected_dates(self, dates):
        """
        Returns range of dates as selected in the URL.

        If no specific dates selected just returns all dates.
        """
        if not self.date_kwargs:
            return dates

        selected_dates = [date for date in dates if date.year == self.current_year]
        current_month = self.get_current_month()

        if current_month is None:
            return selected_dates

        return [date for date in selected_dates if date.month == current_month.month]

    def get_paginated_response(self, data):
        dates = self.get_dates()
        selected_dates = self.get_selected_dates(dates)

        extra = {
            "dates": dates,
            "selected_dates": selected_dates,
            "current_month": self.current_month,
            "current_year": self.current_year,
            "months": self.get_months(dates),
            "years": self.get_years(dates),
            "selected_months": self.get_months(selected_dates),
            "selected_years": self.get_years(selected_dates),
            "reverse_sort_url": self.get_reverse_sort_url(),
            "order": self.sort_order,
            "date_filters": self.date_kwargs,
        }

        return super().get_paginated_response({"items": data, "date_info": extra})


timeline_api_view = TimelineAPIView.as_view()


class PrivateAPIView(BaseActivityStreamAPIView):
    # will fold in SearchMixin later

    search_param = "q"

    @cached_property
    def search_query(self):
        return self.request.GET.get(self.search_param)

    def get_ordering(self):
        if self.search_query:
            return ("-rank", "-created")
        return "-created"

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset).private(self.request.user)
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


private_api_view = PrivateAPIView.as_view()


class ActivityViewSet(ModelViewSet):
    permission_classes = [
        IsCommunityMember,
        IsActivityOwner,
    ]

    def get_queryset(self):
        return (
            self.model.objects.select_related("owner", "editor", "parent__owner")
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
            .order_by("-published", "-created")
        )

    # TBD: moderator delete should be a dedicated endpoint.

    def perform_create(self, serializer):
        obj = serializer.save(
            owner=self.request.user,
            community=self.request.community,
            published=timezone.now() if serializer.data.get("publish") else None,
        )
        if obj.published:
            obj.notify_on_publish()

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        obj = self.get_object()
        if not obj.published:
            obj.published = timezone.now()
            obj.save()
            obj.notify_on_publish()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCommunityMember, IsNotActivityOwner],
    )
    def like(self, request, pk=None):

        obj = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=obj.owner,
                content_object=obj,
            ).notify()

        except IntegrityError:
            # dupe, ignore
            pass

        return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[IsCommunityMember, IsNotActivityOwner],
    )
    def dislike(self, request, pk=None):
        self.get_object().get_likes().filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsCommunityMember])
    def add_bookmark(self, request, pk=None):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.get_object(),
            )
        except IntegrityError:
            # dupe, ignore
            pass
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], permission_classes=[IsCommunityMember])
    def remove_bookmark(self, request, pk=None):
        self.get_object().get_bookmarks().filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsCommunityMember])
    def add_comment(self, request, pk=None):
        obj = self.get_object()
        if not obj.allow_comments():
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(
                owner=request.user, community=request.community, content_object=obj,
            )

            comment.notify_on_create()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
