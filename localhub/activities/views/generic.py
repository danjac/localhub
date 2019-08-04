# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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

from localhub.activities.emails import (
    send_activity_deleted_email,
    send_activity_notification_email,
)
from localhub.activities.models import Activity
from localhub.comments.emails import send_comment_notification_email
from localhub.comments.forms import CommentForm
from localhub.communities.models import Community
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import (
    BaseQuerySetViewMixin,
    BreadcrumbList,
    ContextDict,
)
from localhub.core.views import BreadcrumbsMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like


class ActivityQuerySetMixin(CommunityRequiredMixin, BaseQuerySetViewMixin):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .for_community(self.request.community)
            .select_related("owner", "community", "parent", "parent__owner")
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

    def form_valid(self, form: ModelForm) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        for notification in self.object.notify(created=True):
            send_activity_notification_email(self.object, notification)

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityListView(MultipleActivityMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    order_by = "-id"

    def get_queryset(self) -> QuerySet:
        qs = (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
            .blocked(self.request.user)
            .order_by(self.order_by)
        )

        self.search_query = self.request.GET.get("q")
        if self.search_query:
            qs = qs.search(self.search_query).order_by("rank")
        return qs


class ActivityUpdateView(
    PermissionRequiredMixin, SingleActivityMixin, BreadcrumbsMixin, UpdateView
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")

    def get_breadcrumbs(self) -> BreadcrumbList:
        return self.object.get_breadcrumbs() + [(self.request.path, _("Edit"))]

    def get_success_message(self) -> str:
        return self.success_message

    def form_valid(self, form: ModelForm) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.save()

        for notification in self.object.notify(created=False):
            send_activity_notification_email(self.object, notification)

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityDeleteView(
    PermissionRequiredMixin, SingleActivityMixin, DeleteView
):
    permission_required = "activities.delete_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _("The %s has been deleted")

    def get_success_message(self) -> Optional[str]:
        return self.success_message % self.object._meta.verbose_name

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        if self.request.user != self.object.owner:
            send_activity_deleted_email(self.object)

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

        data["reshares"] = self.get_reshares()

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

    def get_reshares(self) -> QuerySet:
        return (
            self.object.reshares.blocked_users(self.request.user)
            .select_related("owner")
            .order_by("-created")
        )

    def get_comments(self) -> QuerySet:
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.community, self.request.user)
            .blocked_users(self.request.user)
            .filter(owner__communities=self.request.community)
            .select_related("owner", "community")
            .order_by("created")
        )


class ActivityReshareView(PermissionRequiredMixin, SingleActivityView):
    permission_required = "activities.reshare_activity"

    def get_queryset(self) -> QuerySet:
        """
        Make sure user has only reshared once.
        """
        return (
            super()
            .get_queryset()
            .with_has_reshared(self.request.user)
            .filter(has_reshared=False)
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        reshare = self.object.reshare(self.request.user)

        messages.success(
            self.request,
            _("You have reshared this %s") % self.object._meta.verbose_name,
        )

        for notification in reshare.notify(created=True):
            send_activity_notification_email(self.object, notification)

        return HttpResponseRedirect(self.object.get_absolute_url())


class ActivityLikeView(PermissionRequiredMixin, SingleActivityView):
    permission_required = "activities.like_activity"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        try:
            like = Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            )
            for notification in like.notify():
                send_activity_notification_email(self.object, notification)

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

    def form_valid(self, form: ModelForm) -> HttpResponse:
        flag = form.save(commit=False)
        flag.content_object = self.object
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        for notification in flag.notify():
            send_activity_notification_email(self.object, notification)

        messages.success(
            self.request,
            _(
                "This %s has been flagged to the moderators"
                % self.object._meta.verbose_name
            ),
        )
        return HttpResponseRedirect(self.get_success_url())


activity_flag_view = ActivityFlagView.as_view()


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

    def form_valid(self, form: ModelForm) -> HttpResponse:
        comment = form.save(commit=False)
        comment.content_object = self.object
        comment.community = self.request.community
        comment.owner = self.request.user
        comment.save()
        for notification in comment.notify(created=True):
            send_comment_notification_email(comment, notification)
        messages.success(self.request, _("Your comment has been posted"))
        return HttpResponseRedirect(self.get_success_url())
