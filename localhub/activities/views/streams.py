# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional

from django.conf import settings
from django.db.models import QuerySet

from localhub.activities.types import ActivityType
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import QuerySetList
from localhub.core.views import MultipleQuerySetListView, SearchMixin
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.posts.models import Post


class BaseStreamView(CommunityRequiredMixin, MultipleQuerySetListView):
    ordering = "created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models: List[ActivityType] = [Photo, Post, Event]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.for_community(community=self.request.community)

    def get_queryset_for_model(self, model: ActivityType) -> QuerySet:
        return self.filter_queryset(
            model.objects.with_common_annotations(
                self.request.community, self.request.user
            ).select_related("owner", "community", "parent", "parent__owner")
        )

    def get_queryset_count_for_model(self, model: ActivityType) -> QuerySet:
        return self.filter_queryset(model.objects).only("pk")

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset_for_model(model) for model in self.models]

    def get_count_querysets(self) -> QuerySetList:
        return [
            self.get_queryset_count_for_model(model) for model in self.models
        ]


class StreamView(BaseStreamView):
    template_name = "activities/stream.html"

    def filter_queryset(self, queryset) -> QuerySet:
        return (
            super()
            .filter_queryset(queryset)
            .following(self.request.user)
            .blocked(self.request.user)
        )


stream_view = StreamView.as_view()


class SearchView(SearchMixin, BaseStreamView):
    template_name = "activities/search.html"

    def get_ordering(self) -> Optional[str]:
        return "rank" if self.search_query else None

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        if self.search_query:
            return (
                super()
                .filter_queryset(queryset)
                .blocked(self.request.user)
                .search(self.search_query)
            )
        return queryset.none()


search_view = SearchView.as_view()
