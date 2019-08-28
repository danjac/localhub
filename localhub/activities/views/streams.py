# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.utils.formats import date_format
from django.utils.functional import cached_property

from localhub.communities.rules import is_member
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.views import MultipleQuerySetListView, SearchMixin
from localhub.events.models import Event
from localhub.join_requests.models import JoinRequest
from localhub.photos.models import Photo
from localhub.posts.models import Post


class BaseStreamView(CommunityRequiredMixin, MultipleQuerySetListView):
    ordering = "-created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models = [Photo, Post, Event]

    def filter_queryset(self, queryset):
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model):
        return self.filter_queryset(
            model.objects.with_common_annotations(
                self.request.community, self.request.user
            ).select_related("owner", "community", "parent", "parent__owner")
        )

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects)

    def get_querysets(self):
        return [self.get_queryset_for_model(model) for model in self.models]

    def get_count_querysets(self):
        return [
            self.get_count_queryset_for_model(model) for model in self.models
        ]


class StreamView(BaseStreamView):
    template_name = "activities/stream.html"

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .following(self.request.user)
            .blocked(self.request.user)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["join_request_sent"] = (
            self.request.user.is_authenticated
            and not is_member(self.request.user, self.request.community)
            and JoinRequest.objects.filter(
                sender=self.request.user,
                community=self.request.community,
                status=JoinRequest.STATUS.pending,
            ).exists()
        )

        return data


stream_view = StreamView.as_view()


class TimelineView(StreamView):
    template_name = "activities/timeline.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE * 2

    """
    TBD: call queryset.dates() to get the list of years/months
    and allow for specific year/month links on this page.

    For current year, show individual months in one row
    Underneath show previous/future years.
    """

    @cached_property
    def sort_by_ascending(self):
        return self.request.GET.get("order") == "asc"

    def get_ordering(self):
        return "created" if self.sort_by_ascending else "-created"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        for object in data["object_list"]:
            object["month"] = date_format(object["created"], "F Y")
        return data


timeline_view = TimelineView.as_view()


class SearchView(SearchMixin, BaseStreamView):
    template_name = "activities/search.html"

    def get_ordering(self):
        return ("-rank", "-created") if self.search_query else None

    def filter_queryset(self, queryset):
        if self.search_query:
            return (
                super()
                .filter_queryset(queryset)
                .blocked(self.request.user)
                .search(self.search_query)
            )
        return queryset.none()


search_view = SearchView.as_view()
