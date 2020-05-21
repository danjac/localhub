# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.utils.functional import cached_property

# Django Rest Framework
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Social-BFG
from social_bfg.apps.communities.permissions import IsCommunity, IsCommunityMember
from social_bfg.apps.events.models import Event
from social_bfg.apps.events.serializers import EventSerializer
from social_bfg.apps.photos.models import Photo
from social_bfg.apps.photos.serializers import PhotoSerializer
from social_bfg.apps.polls.models import Poll
from social_bfg.apps.polls.serializers import PollSerializer
from social_bfg.apps.posts.models import Post
from social_bfg.apps.posts.serializers import PostSerializer
from social_bfg.pagination import PresetCountPaginator

# Local
from ..utils import get_activity_queryset_count, get_activity_querysets, load_objects


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
        IsAuthenticated,
        IsCommunity,
        IsCommunityMember,
    ]

    # may need modification
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


class DefaultStreamAPIView(BaseActivityStreamAPIView):
    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .with_activity_stream_filters(self.request.user)
            .exclude_blocked(self.request.user)
        )


default_stream_api_view = DefaultStreamAPIView.as_view()
