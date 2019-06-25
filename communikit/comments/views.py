# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import no_type_check

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import (
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

from communikit.activities.models import Activity
from communikit.activities.views import SingleActivityMixin
from communikit.comments.emails import send_deletion_email
from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment, Like
from communikit.communities.views import CommunityRequiredMixin
from communikit.core.types import BreadcrumbList, ContextDict
from communikit.core.views import BreadcrumbsMixin
from communikit.flags.forms import FlagForm
from communikit.users.views import UserProfileMixin


class CommentQuerySetMixin(CommunityRequiredMixin):
    @no_type_check
    def get_queryset(self) -> QuerySet:
        return (
            Comment.objects.get_queryset()
            .filter(activity__community=self.request.community)
            .select_related("owner", "activity", "activity__community")
        )


class MultipleCommentMixin(CommentQuerySetMixin, MultipleObjectMixin):
    ...


class SingleCommentMixin(CommentQuerySetMixin, SingleObjectMixin):
    ...


class CommentParentMixin:
    @cached_property
    def parent(self) -> Activity:
        return Activity.objects.select_related(
            "community", "owner"
        ).get_subclass(pk=self.object.activity_id)

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        return data


class SingleCommentView(SingleCommentMixin, View):
    ...


class CommentCreateView(
    PermissionRequiredMixin, SingleActivityMixin, FormView
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "comments.create_comment"
    model = Activity

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().select_subclasses()

    def get_permission_object(self) -> Activity:
        return self.object

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        comment = form.save(commit=False)
        comment.activity = self.object
        comment.owner = self.request.user
        comment.save()
        messages.success(self.request, _("Your comment has been posted"))
        return HttpResponseRedirect(self.get_success_url())


comment_create_view = CommentCreateView.as_view()


class CommentDetailView(
    CommentQuerySetMixin, CommentParentMixin, BreadcrumbsMixin, DetailView
):
    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.parent.get_breadcrumbs() + [
            (self.request.path, _("Comment"))
        ]

    def get_flags(self) -> QuerySet:
        return (
            self.object.get_flags().select_related("user").order_by("-created")
        )

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()
        return data


comment_detail_view = CommentDetailView.as_view()


class CommentUpdateView(
    PermissionRequiredMixin,
    CommentQuerySetMixin,
    CommentParentMixin,
    BreadcrumbsMixin,
    UpdateView,
):
    form_class = CommentForm
    permission_required = "comments.change_comment"

    def get_success_url(self) -> str:
        return self.parent.get_absolute_url()

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.parent.get_breadcrumbs() + [
            (self.request.path, _("Edit Comment"))
        ]


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin,
    CommentQuerySetMixin,
    CommentParentMixin,
    DeleteView,
):
    permission_required = "comments.delete_comment"

    def get_success_url(self) -> str:
        return self.parent.get_absolute_url()

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        if request.user != self.object.owner:
            send_deletion_email(self.object)

        messages.success(request, _("Comment has been deleted"))
        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()


class CommentLikeView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleCommentView
):
    permission_required = "comments.like_comment"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        try:
            Like.objects.create(user=request.user, comment=self.object)
        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(LoginRequiredMixin, SingleCommentView):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        Like.objects.filter(user=request.user, comment=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


class CommentFlagView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleCommentMixin,
    BreadcrumbsMixin,
    CommentParentMixin,
    FormView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"
    permission_required = "comments.flag_comment"

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

    def get_permission_object(self) -> Comment:
        return self.object

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.parent.get_breadcrumbs() + [
            (self.request.path, _("Flag Comment"))
        ]

    def get_success_url(self) -> str:
        return self.parent.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        flag = form.save(commit=False)
        flag.content_object = self.object
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()
        messages.success(
            self.request, _("This comment has been flagged to the moderators")
        )
        return HttpResponseRedirect(self.get_success_url())


comment_flag_view = CommentFlagView.as_view()


class CommentProfileView(MultipleCommentMixin, UserProfileMixin, ListView):
    active_tab = "comments"
    template_name = "comments/profile.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(owner=self.object)
            .with_common_annotations(self.request.community, self.request.user)
            .order_by("-created")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = Like.objects.filter(
            comment__owner=self.object
        ).count()
        return data


comment_profile_view = CommentProfileView.as_view()
