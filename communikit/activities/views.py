# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional, Type, no_type_check

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import URLPattern, path, reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
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

# from silk.profiling.profiler import silk_profile

from communikit.activities.models import Activity, Like
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import (
    BreadcrumbList,
    ContextDict,
    HttpRequestResponse,
    QuerySetList,
)
from communikit.core.views import CombinedQuerySetListView
from communikit.events.models import Event
from communikit.photos.models import Photo
from communikit.posts.models import Post
from communikit.users.views import UserProfileMixin


class BreadcrumbsMixin:
    breadcrumbs: Optional[BreadcrumbList] = None

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.breadcrumbs or []

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data()
        data["breadcrumbs"] = self.get_breadcrumbs()
        return data


class ActivityQuerySetMixin(CommunityRequiredMixin):
    @no_type_check
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(community=self.request.community)
            .select_related("owner", "community")
        )


class SingleActivityMixin(ActivityQuerySetMixin, SingleObjectMixin):
    ...


class MultipleActivityMixin(ActivityQuerySetMixin, MultipleObjectMixin):
    ...


class SingleActivityView(SingleActivityMixin, View):
    ...


class ActivityCreateView(
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    BreadcrumbsMixin,
    CreateView,
):
    permission_required = "activities.create_activity"
    success_message = _("Your update has been posted")

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_success_message(self) -> str:
        return self.success_message

    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("activities:stream"), _("Home")),
            (
                reverse(self.model.list_url_name),
                _(self.model._meta.verbose_name_plural.title()),
            ),
            (self.request.path, _("Submit")),
        ]

    def form_valid(self, form) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityListView(MultipleActivityMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
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
    BreadcrumbsMixin,
    UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.object.get_breadcrumbs() + [(self.request.path, _("Edit"))]


class ActivityDeleteView(
    PermissionRequiredMixin, SingleActivityMixin, DeleteView
):
    permission_required = "activities.delete_activity"
    success_url = reverse_lazy("activities:stream")
    success_message = _("Your %s has been deleted")

    def get_success_message(self) -> Optional[str]:
        return self.success_message % self.object._meta.verbose_name

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class ActivityDetailView(SingleActivityMixin, BreadcrumbsMixin, DetailView):
    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.object.get_breadcrumbs()

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
            data.update(
                {
                    "comment_form": CommentForm(),
                    "create_comment_url": reverse(
                        "comments:create", args=[self.object.id]
                    ),
                }
            )

        return data


class ActivityLikeView(PermissionRequiredMixin, SingleActivityView):
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


class ActivityDislikeView(LoginRequiredMixin, SingleActivityView):
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
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models: List[Type[Activity]] = [Photo, Post, Event]

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return (
            model.objects.filter(community=self.request.community)
            .with_num_comments()
            .with_num_likes()
            .with_has_liked(self.request.user)
            .select_related("owner", "community")
        )

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset(model) for model in self.models]


activity_stream_view = ActivityStreamView.as_view()


class ActivitySearchView(ActivityStreamView):
    template_name = "activities/search.html"

    def get_ordering(self) -> Optional[str]:
        return "rank" if self.search_query else None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.search_query = request.GET.get("q", "").strip()
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

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = Like.objects.filter(
            activity__owner=self.object
        ).count()
        return data


activity_profile_view = ActivityProfileView.as_view()


class ActivityViewSet:

    model = None
    form_class = None

    create_view_class = ActivityCreateView
    delete_view_class = ActivityDeleteView
    detail_view_class = ActivityDetailView
    dislike_view_class = ActivityDislikeView
    like_view_class = ActivityLikeView
    list_view_class = ActivityListView
    update_view_class = ActivityUpdateView

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def create_view(self) -> HttpRequestResponse:
        return self.create_view_class.as_view(
            model=self.model, form_class=self.form_class
        )

    @property
    def update_view(self) -> HttpRequestResponse:
        return self.update_view_class.as_view(
            model=self.model, form_class=self.form_class
        )

    @property
    def list_view(self) -> HttpRequestResponse:
        return self.list_view_class.as_view(model=self.model)

    @property
    def detail_view(self) -> HttpRequestResponse:
        return self.detail_view_class.as_view(model=self.model)

    @property
    def delete_view(self) -> HttpRequestResponse:
        return self.delete_view_class.as_view(model=self.model)

    @property
    def like_view(self) -> HttpRequestResponse:
        return self.like_view_class.as_view(model=self.model)

    @property
    def dislike_view(self) -> HttpRequestResponse:
        return self.dislike_view_class.as_view(model=self.model)

    @property
    def urls(self) -> List[URLPattern]:
        return [
            path("", self.list_view, name="list"),
            path("~create", self.create_view, name="create"),
            path("<int:pk>/~update/", self.update_view, name="update"),
            path("<int:pk>/~delete/", self.delete_view, name="delete"),
            path("<int:pk>/~like/", self.like_view, name="like"),
            path("<int:pk>/~dislike/", self.dislike_view, name="dislike"),
            path("<int:pk>/<slug:slug>/", self.detail_view, name="detail"),
        ]
