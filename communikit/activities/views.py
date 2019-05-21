# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict
from typing import Dict, Type


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Page, Paginator
from django.db import IntegrityError
from django.db.models import CharField, QuerySet, Value
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities import app_settings
from communikit.activities.models import Activity, Like
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.events.models import Event
from communikit.posts.models import Post
from communikit.types import ContextDict


class ActivityQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(community=self.request.community)
            .select_related("owner", "community")
        )


class BaseActivityCreateView(
    CommunityRequiredMixin, PermissionRequiredMixin, CreateView
):
    permission_required = "activities.create_activity"
    success_url = reverse_lazy("activities:stream")
    success_message = _("Your update has been posted")

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_success_message(self) -> str:
        return self.success_message

    def form_valid(self, form) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class BaseActivityListView(ActivityQuerySetMixin, ListView):
    allow_empty = True
    paginate_by = app_settings.COMMUNIKIT_ACTIVITIES_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
        )


class BaseActivityUpdateView(
    PermissionRequiredMixin,
    SuccessMessageMixin,
    ActivityQuerySetMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")


class BaseActivityDeleteView(
    PermissionRequiredMixin, ActivityQuerySetMixin, DeleteView
):
    permission_required = "activities.delete_activity"
    success_url = reverse_lazy("activities:stream")
    success_message = None

    def get_success_message(self):
        return self.success_message

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class BaseActivityDetailView(ActivityQuerySetMixin, DetailView):
    def get_comments(self) -> QuerySet:
        return (
            self.object.comment_set.select_related(
                "owner", "activity", "activity__community"
            )
            .with_num_likes()
            .with_has_liked(self.request.user)
            .order_by("created")
        )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["comments"] = self.get_comments()
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data


class BaseActivityLikeView(
    ActivityQuerySetMixin, PermissionRequiredMixin, SingleObjectMixin, View
):
    permission_required = "activities.like_activity"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        try:
            Like.objects.create(user=request.user, activity=self.object)
        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())


class BaseActivityDislikeView(
    ActivityQuerySetMixin, LoginRequiredMixin, SingleObjectMixin, View
):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        Like.objects.filter(user=request.user, activity=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class ActivityStreamView(CommunityRequiredMixin, TemplateView):
    template_name = "activities/stream.html"
    order_field = "created"
    models = (Post, Event)
    allow_empty = True
    paginate_by = app_settings.COMMUNIKIT_ACTIVITIES_PAGE_SIZE

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return (
            model.objects.filter(community=self.request.community)
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
            .select_related("owner", "community")
        )

    def get_queryset_dict(self) -> Dict[str, QuerySet]:
        return {
            model._meta.model_name: self.get_queryset(model)
            for model in self.models
        }

    def get_pagination_kwargs(self) -> ContextDict:
        return {
            "per_page": self.paginate_by,
            "allow_empty_first_page": self.allow_empty,
        }

    def get_page(self) -> Page:
        """
        https://simonwillison.net/2018/Mar/25/combined-recent-additions/
        """
        queryset_dict = self.get_queryset_dict()

        querysets = [
            qs.annotate(
                activity_type=Value(key, output_field=CharField())
            ).values("pk", "activity_type", self.order_field)
            for key, qs in queryset_dict.items()
        ]
        union_qs = (
            querysets[0].union(*querysets[1:]).order_by(f"-{self.order_field}")
        )
        page = Paginator(union_qs, **self.get_pagination_kwargs()).get_page(
            self.request.GET.get("page", 1)
        )

        bulk_load = defaultdict(set)

        for item in page:
            bulk_load[item["activity_type"]].add(item["pk"])

        fetched = {
            (activity_type, activity.pk): activity
            for activity_type, pks in bulk_load.items()
            for activity in queryset_dict[activity_type].filter(pk__in=pks)
        }

        for item in page:
            item["object"] = fetched[(item["activity_type"], item["pk"])]

        return page

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        page = self.get_page()
        data.update(
            {
                "page": page,
                "paginator": page.paginator,
                "object_list": page.object_list,
                "is_paginated": page.has_other_pages(),
            }
        )
        return data


activity_stream_view = ActivityStreamView.as_view()


class ActivitySearchView(ActivityStreamView):
    template_name = "activities/search.html"
    order_field = "rank"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.search_query = request.GET.get("q").strip()
        return super().get(request, *args, **kwargs)

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        if self.search_query:
            return super().get_queryset(model).search(self.search_query)
        return model.objects.none()

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["search_query"] = self.search_query
        return data


activity_search_view = ActivitySearchView.as_view()
