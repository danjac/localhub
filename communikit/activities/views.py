# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional, Type, no_type_check

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities import app_settings
from communikit.activities.models import Activity, Like
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import ContextDict, QuerySetList
from communikit.core.views import CombinedQuerySetListView
from communikit.events.models import Event
from communikit.posts.models import Post
from communikit.users.views import UserProfileMixin


class ActivityQuerySetMixin:
    @no_type_check
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(community=self.request.community)
            .select_related("owner", "community")
        )


class SingleActivityMixin(
    CommunityRequiredMixin, ActivityQuerySetMixin, SingleObjectMixin
):
    ...


class MultipleActivityMixin(
    CommunityRequiredMixin, ActivityQuerySetMixin, MultipleObjectMixin
):
    ...


class ActivityCreateView(
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


class ActivityListView(MultipleActivityMixin, ListView):
    allow_empty = True
    paginate_by = app_settings.DEFAULT_PAGE_SIZE
    order_by = "-created"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
            .order_by(self.order_by)
        )


class ActivityUpdateView(
    PermissionRequiredMixin,
    SuccessMessageMixin,
    SingleActivityMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")


class ActivityDeleteView(
    PermissionRequiredMixin, SingleActivityMixin, DeleteView
):
    permission_required = "activities.delete_activity"
    success_url = reverse_lazy("activities:stream")
    success_message: Optional[str] = None

    def get_success_message(self) -> Optional[str]:
        return self.success_message

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class ActivityDetailView(SingleActivityMixin, DetailView):
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


class ActivityLikeView(PermissionRequiredMixin, SingleActivityMixin, View):
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


class ActivityDislikeView(LoginRequiredMixin, SingleActivityMixin, View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        Like.objects.filter(user=request.user, activity=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class ActivityStreamView(CommunityRequiredMixin, CombinedQuerySetListView):
    template_name = "activities/stream.html"
    ordering = "created"
    allow_empty = True
    paginate_by = app_settings.DEFAULT_PAGE_SIZE

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return (
            model.objects.filter(community=self.request.community)
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
            .select_related("owner", "community")
        )

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset(model) for model in (Post, Event)]


activity_stream_view = ActivityStreamView.as_view()


class ActivitySearchView(ActivityStreamView):
    template_name = "activities/search.html"
    ordering = "rank"

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


class ActivityProfileView(UserProfileMixin, ActivityStreamView):
    active_tab = "posts"
    template_name = "activities/profile.html"

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return super().get_queryset(model).filter(owner=self.object)


activity_profile_view = ActivityProfileView.as_view()
