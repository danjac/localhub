# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator


from functools import reduce

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Q, QuerySet, Value
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, View
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from taggit.models import Tag, TaggedItem


from localhub.activities.types import ActivityType
from localhub.activities.views.streams import BaseStreamView
from localhub.communities.models import Community
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import ContextDict
from localhub.core.utils.content_types import get_generic_related_exists
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.posts.models import Post
from localhub.subscriptions.models import Subscription


class TagQuerySetMixin(CommunityRequiredMixin):
    tagged_models = [Post, Event, Photo]

    def get_queryset(self) -> QuerySet:
        q = Q(
            reduce(
                operator.or_,
                [
                    Q(
                        object_id__in=model.objects.filter(
                            community=self.request.community
                        ).values("id"),
                        content_type=content_type,
                    )
                    for model, content_type in ContentType.objects.get_for_models(  # noqa
                        *self.tagged_models
                    ).items()
                ],
            )
        )

        return (
            Tag.objects.filter(
                taggit_taggeditem_items__in=TaggedItem.objects.filter(q)
            )
            .order_by("name")
            .distinct()
        )


class SingleTagMixin(TagQuerySetMixin, SingleObjectMixin):
    ...


class SingleTagView(SingleTagMixin, View):
    ...


class BaseTagListView(TagQuerySetMixin, ListView):
    ...


class TagAutocompleteListView(BaseTagListView):
    template_name = "activities/tags/tag_autocomplete_list.html"

    def get_queryset(self) -> QuerySet:
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Tag.objects.none()
        return super().get_queryset().filter(name__istartswith=search_term)


tag_autocomplete_list_view = TagAutocompleteListView.as_view()


class TagDetailView(SingleTagMixin, BaseStreamView):
    template_name = "activities/tags/tag_detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_queryset_for_model(self, model: ActivityType) -> QuerySet:
        return (
            super()
            .get_queryset_for_model(model)
            .filter(tags__name__in=[self.object.name])
            .distinct()
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["tag"] = self.object
        return data


tag_detail_view = TagDetailView.as_view()


class TagFollowView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleTagView
):
    permission_required = "subscriptions.create_subscription"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_success_url(self) -> str:
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        Subscription.objects.create(
            subscriber=self.request.user,
            content_object=self.object,
            community=self.request.community,
        )

        messages.success(self.request, _("You are now following this tag"))
        return HttpResponseRedirect(self.get_success_url())


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(LoginRequiredMixin, SingleTagView):
    def get_success_url(self) -> str:
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        Subscription.objects.filter(
            object_id=self.object.id,
            content_type=ContentType.objects.get_for_model(self.object),
            subscriber=self.request.user,
        ).delete()
        messages.success(
            self.request, _("You have stopped following this tag")
        )
        return HttpResponseRedirect(self.get_success_url())


tag_unfollow_view = TagUnfollowView.as_view()


class TagListView(BaseTagListView):
    template_name = "activities/tags/tag_list.html"

    def get_queryset(self) -> QuerySet:

        qs = super().get_queryset()

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_subscribed=get_generic_related_exists(
                    Tag,
                    Subscription.objects.filter(
                        subscriber=self.request.user,
                        community=self.request.community,
                    ),
                )
            )
        else:
            qs = qs.annotate(is_subscribed=Value(False, BooleanField()))

        return qs


tag_list_view = TagListView.as_view()


class FollowingTagListView(LoginRequiredMixin, TagListView):
    template_name = "activities/tags/following_tag_list.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_subscribed=True)


following_tag_list_view = FollowingTagListView.as_view()
