# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional

from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse

from localhub.activities.types import ActivityType
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import ContextDict, QuerySetList
from localhub.core.views import MultipleQuerySetListView
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.posts.models import Post


class BaseStreamView(CommunityRequiredMixin, MultipleQuerySetListView):
    ordering = "created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models: List[ActivityType] = [Photo, Post, Event]

    def get_queryset_for_model(self, model: ActivityType) -> QuerySet:
        return (
            model.objects.for_community(community=self.request.community)
            .with_common_annotations(self.request.community, self.request.user)
            .select_related("owner", "community")
        )

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset_for_model(model) for model in self.models]


class StreamView(BaseStreamView):
    template_name = "activities/stream.html"

    def get_queryset_for_model(self, model: ActivityType) -> QuerySet:
        qs = super().get_queryset_for_model(model)

        self.show_all = (
            "following" not in self.request.GET
            or self.request.user.is_anonymous
        )
        if self.show_all:
            return qs
        return qs.following(self.request.user)


stream_view = StreamView.as_view()


class SearchView(BaseStreamView):
    template_name = "activities/search.html"

    def get_ordering(self) -> Optional[str]:
        return "rank" if self.search_query else None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.search_query = request.GET.get("q", "").strip()
        return super().get(request, *args, **kwargs)

    def get_queryset_for_model(self, model: ActivityType) -> QuerySet:
        if self.search_query:
            return (
                super().get_queryset_for_model(model).search(self.search_query)
            )
        return model.objects.none()

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["search_query"] = self.search_query
        return data


search_view = SearchView.as_view()
