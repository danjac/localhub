# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator


from functools import reduce

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
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
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.posts.models import Post
from localhub.subscriptions.models import Subscription


class TagAutocompleteListView(CommunityRequiredMixin, ListView):
    template_name = "activities/tag_autocomplete_list.html"

    def get_queryset(self) -> QuerySet:
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Tag.objects.none()

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
                        Post, Event, Photo
                    ).items()
                ],
            )
        )

        return (
            Tag.objects.filter(
                taggit_taggeditem_items__in=TaggedItem.objects.filter(q),
                name__istartswith=search_term,
            )
            .order_by("name")
            .distinct()
        )


tag_autocomplete_list_view = TagAutocompleteListView.as_view()


class SingleTagMixin(SingleObjectMixin):
    model = Tag


class TagDetailView(SingleTagMixin, BaseStreamView):
    template_name = "activities/tag_detail.html"

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

    def is_subscribed(self):
        if not self.request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            content_type=ContentType.objects.get_for_model(self.object),
            object_id=self.object.id,
            subscriber=self.request.user,
            community=self.request.community,
        ).exists()

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["tag"] = self.object
        data["is_subscribed"] = self.is_subscribed()
        return data


tag_detail_view = TagDetailView.as_view()


class TagSubscribeView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleTagMixin, View
):
    permission_required = "subscriptions.create_subscription"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_success_url(self) -> str:
        return reverse("activities:tag", args=[self.object.slug])

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        Subscription.objects.create(
            subscriber=self.request.user,
            content_object=self.object,
            community=self.request.community,
        )

        messages.success(self.request, _("You are now following this tag"))
        return HttpResponseRedirect(self.get_success_url())


tag_subscribe_view = TagSubscribeView.as_view()


class TagUnsubscribeView(LoginRequiredMixin, SingleTagMixin, View):
    def get_success_url(self) -> str:
        return reverse("activities:tag", args=[self.object.slug])

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


tag_unsubscribe_view = TagUnsubscribeView.as_view()
