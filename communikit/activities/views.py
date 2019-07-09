# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from typing import List, Optional, Type, no_type_check

from functools import reduce

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import URLPattern, path, reverse
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

from taggit.models import Tag, TaggedItem

from communikit.activities.models import Activity
from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import (
    BreadcrumbList,
    ContextDict,
    DjangoView,
    QuerySetList,
)
from communikit.core.views import BreadcrumbsMixin, MultipleQuerySetListView
from communikit.events.models import Event
from communikit.flags.forms import FlagForm
from communikit.likes.models import Like
from communikit.photos.models import Photo
from communikit.posts.models import Post
from communikit.subscriptions.models import Subscription


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
        qs = (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
            .order_by(self.order_by)
        )
        self.show_all = (
            "following" not in self.request.GET
            or self.request.user.is_anonymous
        )
        if self.show_all:
            return qs
        return qs.following(self.request.user)


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


class BaseActivityStreamView(CommunityRequiredMixin, MultipleQuerySetListView):
    ordering = "created"
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    models: List[Type[Activity]] = [Photo, Post, Event]

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
        return (
            model.objects.filter(community=self.request.community)
            .with_common_annotations(self.request.community, self.request.user)
            .select_related("owner", "community")
        )

    def get_querysets(self) -> QuerySetList:
        return [self.get_queryset_for_model(model) for model in self.models]


class ActivityStreamView(BaseActivityStreamView):
    template_name = "activities/stream.html"

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
        qs = super().get_queryset_for_model(model)

        self.show_all = (
            "following" not in self.request.GET
            or self.request.user.is_anonymous
        )
        if self.show_all:
            return qs
        return qs.following(self.request.user)


activity_stream_view = ActivityStreamView.as_view()


class SingleTagMixin(SingleObjectMixin):
    model = Tag


class ActivityTagView(SingleTagMixin, BaseActivityStreamView):
    template_name = "activities/tag_detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
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


activity_tag_view = ActivityTagView.as_view()


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


class ActivitySearchView(BaseActivityStreamView):
    template_name = "activities/search.html"

    def get_ordering(self) -> Optional[str]:
        return "rank" if self.search_query else None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.search_query = request.GET.get("q", "").strip()
        return super().get(request, *args, **kwargs)

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
        if self.search_query:
            return (
                super().get_queryset_for_model(model).search(self.search_query)
            )
        return model.objects.none()

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["search_query"] = self.search_query
        return data


activity_search_view = ActivitySearchView.as_view()


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
    def create_view(self) -> DjangoView:
        return self.create_view_class.as_view(
            model=self.model, form_class=self.form_class
        )

    @property
    def create_comment_view(self) -> DjangoView:
        return self.create_comment_view_class.as_view(model=self.model)

    @property
    def update_view(self) -> DjangoView:
        return self.update_view_class.as_view(
            model=self.model, form_class=self.form_class
        )

    @property
    def list_view(self) -> DjangoView:
        return self.list_view_class.as_view(model=self.model)

    @property
    def detail_view(self) -> DjangoView:
        return self.detail_view_class.as_view(model=self.model)

    @property
    def delete_view(self) -> DjangoView:
        return self.delete_view_class.as_view(model=self.model)

    @property
    def like_view(self) -> DjangoView:
        return self.like_view_class.as_view(model=self.model)

    @property
    def dislike_view(self) -> DjangoView:
        return self.dislike_view_class.as_view(model=self.model)

    @property
    def flag_view(self) -> DjangoView:
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
