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
from django.urls import URLPattern, path
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities.models import Activity  # , Like
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import (
    BreadcrumbList,
    ContextDict,
    HttpRequestResponse,
    QuerySetList,
)
from communikit.core.views import BreadcrumbsMixin, CombinedQuerySetListView
from communikit.events.models import Event
from communikit.flags.forms import FlagForm
from communikit.likes.models import Like
from communikit.photos.models import Photo
from communikit.posts.models import Post
from communikit.users.views import UserProfileMixin


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
        return self.model.get_breadcrumbs_for_model() + [
            (self.request.path, _("Submit"))
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
            .with_common_annotations(self.request.community, self.request.user)
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
    success_url = settings.HOME_PAGE_URL
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
    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()

        data["comments"] = self.get_comments()
        if self.request.user.has_perm(
            "activities.create_comment", self.object
        ):
            data.update({"comment_form": CommentForm()})

        return data

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
        )

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.object.get_breadcrumbs()

    def get_flags(self) -> QuerySet:
        return (
            self.object.get_flags().select_related("user").order_by("-created")
        )

    def get_comments(self) -> QuerySet:
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.community, self.request.user)
            .select_related("owner", "community")
            .order_by("created")
        )


class ActivityLikeView(PermissionRequiredMixin, SingleActivityView):
    permission_required = "activities.like_activity"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            )
        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())


class ActivityDislikeView(LoginRequiredMixin, SingleActivityView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.get_likes().filter(user=request.user).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


class ActivityFlagView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleActivityMixin,
    BreadcrumbsMixin,
    FormView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"
    permission_required = "activities.flag_activity"

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self) -> Activity:
        return self.object

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.object.get_breadcrumbs() + [(self.request.path, _("Flag"))]

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        flag = form.save(commit=False)
        flag.content_object = self.object
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()
        messages.success(
            self.request,
            _(
                "This %s has been flagged to the moderators"
                % self.object._meta.verbose_name
            ),
        )
        return HttpResponseRedirect(self.get_success_url())


activity_flag_view = ActivityFlagView.as_view()


class ActivityStreamView(CommunityRequiredMixin, CombinedQuerySetListView):
    template_name = "activities/stream.html"
    ordering = "created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models: List[Type[Activity]] = [Photo, Post, Event]

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return (
            model.objects.filter(community=self.request.community)
            .with_common_annotations(self.request.community, self.request.user)
            .select_related("owner", "community")
        )

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset(model) for model in self.models]


activity_stream_view = ActivityStreamView.as_view()


class ActivityTagView(ActivityStreamView):

    template_name = "activities/tag.html"

    def get_queryset(self, model: Type[Activity]) -> QuerySet:
        return (
            super()
            .get_queryset(model)
            .filter(tags__name__in=[self.kwargs["tag"]])
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["tag"] = self.kwargs["tag"]
        return data


activity_tag_view = ActivityTagView.as_view()


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
        data["num_likes"] = (
            Like.objects.for_models(*self.models)
            .filter(
                recipient=self.object, community=self.request.community
            )
            .count()
        )
        return data


activity_profile_view = ActivityProfileView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, SingleActivityMixin, FormView
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"
    model = Activity

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self) -> Activity:
        return self.object

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        comment = form.save(commit=False)
        comment.content_object = self.object
        comment.community = self.request.community
        comment.owner = self.request.user
        comment.save()
        messages.success(self.request, _("Your comment has been posted"))
        return HttpResponseRedirect(self.get_success_url())


class ActivityViewSet:

    model = None
    form_class = None
    url_prefix = None

    create_view_class = ActivityCreateView
    create_comment_view_class = ActivityCommentCreateView
    delete_view_class = ActivityDeleteView
    detail_view_class = ActivityDetailView
    dislike_view_class = ActivityDislikeView
    flag_view_class = ActivityFlagView
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
    def create_comment_view(self) -> HttpRequestResponse:
        return self.create_comment_view_class.as_view(model=self.model)

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
    def flag_view(self) -> HttpRequestResponse:
        return self.flag_view_class.as_view(model=self.model)

    @property
    def urls(self) -> List[URLPattern]:
        return [
            path("", self.list_view, name="list"),
            path("~create", self.create_view, name="create"),
            path(
                "<int:pk>/~comment/", self.create_comment_view, name="comment"
            ),
            path("<int:pk>/~delete/", self.delete_view, name="delete"),
            path("<int:pk>/~dislike/", self.dislike_view, name="dislike"),
            path("<int:pk>/~flag/", self.flag_view, name="flag"),
            path("<int:pk>/~like/", self.like_view, name="like"),
            path("<int:pk>/~update/", self.update_view, name="update"),
            path("<int:pk>/<slug:slug>/", self.detail_view, name="detail"),
        ]
