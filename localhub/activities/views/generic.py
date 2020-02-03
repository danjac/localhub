# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    GenericModelView,
    ListView,
    UpdateView,
)

from localhub.comments.forms import CommentForm
from localhub.comments.notifications import send_comment_notifications
from localhub.communities.views import CommunityRequiredMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like
from localhub.views import BreadcrumbsMixin, SearchMixin

from ..notifications import send_activity_deleted_email, send_activity_notifications
from ..utils import get_breadcrumbs_for_instance, get_breadcrumbs_for_model


class ActivityQuerySetMixin(CommunityRequiredMixin):
    model = None

    def get_queryset(self):
        return self.model._default_manager.for_community(
            self.request.community
        ).select_related("owner", "community", "parent", "parent__owner")


class BaseSingleActivityView(ActivityQuerySetMixin, GenericModelView):
    ...


class ActivityCreateView(
    CommunityRequiredMixin, PermissionRequiredMixin, BreadcrumbsMixin, CreateView,
):
    permission_required = "activities.create_activity"
    page_title = _("Submit")

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        message = (
            _("Your %(activity)s has been published")
            if self.object.published
            else _("Your %(activity)s has been saved to Drafts")
        )
        return message % {"activity": self.object._meta.verbose_name}

    def get_breadcrumbs(self):
        return get_breadcrumbs_for_model(self.model) + [
            (
                None,
                _("New %(activity_name)s")
                % {"activity_name": self.model._meta.verbose_name.capitalize()},
            )
        ]

    def form_valid(self, form):

        publish = "save_as_draft" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            for notification in self.object.notify_on_create():
                send_activity_notifications(self.object, notification)

        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


class ActivityListView(ActivityQuerySetMixin, SearchMixin, ListView):
    allow_empty = True
    paginate_by = settings.DEFAULT_PAGE_SIZE
    order_by = ("-published", "-created")

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .published()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked(self.request.user)
            .order_by(*self.order_by)
        )

        if self.search_query:
            qs = qs.search(self.search_query).order_by("-rank", *self.order_by)
        return qs


class ActivityUpdateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, BreadcrumbsMixin, UpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your changes have been saved")
    page_title = _("Edit")

    def get_breadcrumbs(self):
        return get_breadcrumbs_for_instance(self.object) + [
            (
                None,
                _(
                    "Edit %(activity_name)s"
                    % {
                        "activity_name": self.object._meta.verbose_name.capitalize()  # noqa
                    }
                ),
            )
        ]

    def get_success_message(self, publish):
        message = (
            _("Your %(activity)s has been published")
            if publish
            else _("Your %(activity)s has been updated")
        )
        return message % {"activity": self.object._meta.verbose_name}

    def form_valid(self, form):

        publish = (
            not (self.object.published) and "save_as_draft" not in self.request.POST
        )

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        if publish:
            self.object.published = timezone.now()
        self.object.save()

        if self.object.published:
            for notification in self.object.notify_on_update():
                send_activity_notifications(self.object, notification)

        messages.success(self.request, self.get_success_message(publish))
        return HttpResponseRedirect(self.get_success_url())


class ActivityDeleteView(PermissionRequiredMixin, ActivityQuerySetMixin, DeleteView):
    permission_required = "activities.delete_activity"
    success_url = settings.HOME_PAGE_URL
    success_message = _("The %s has been deleted")

    def get_success_message(self):
        return self.success_message % self.object._meta.verbose_name

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        if self.request.user != self.object.owner:
            send_activity_deleted_email(self.object)

        message = self.get_success_message()
        if message:
            messages.success(self.request, message)

        return HttpResponseRedirect(self.get_success_url())


class ActivityDetailView(ActivityQuerySetMixin, BreadcrumbsMixin, DetailView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()

        data["comments"] = self.get_comments()
        if self.request.user.has_perm("activities.create_comment", self.object):
            data.update({"comment_form": CommentForm()})

        data["reshares"] = self.get_reshares()

        return data

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .published_or_owner(self.request.user)
            .with_common_annotations(self.request.user, self.request.community)
        )

    def get_breadcrumbs(self):
        return get_breadcrumbs_for_instance(self.object)

    def get_flags(self):
        return self.object.get_flags().select_related("user").order_by("-created")

    def get_reshares(self):
        return (
            self.object.reshares.for_community(self.request.community)
            .exclude_blocked_users(self.request.user)
            .select_related("owner")
            .order_by("-created")
        )

    def get_comments(self):
        return (
            self.object.get_comments()
            .with_common_annotations(self.request.user, self.request.community)
            .for_community(self.request.community)
            .select_related(
                "owner", "community", "parent", "parent__owner", "parent__community",
            )
            .order_by("created")
        )


class ActivityReshareView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.reshare_activity"

    def get_queryset(self):
        """
        Make sure user has only reshared once.
        """
        return (
            super()
            .get_queryset()
            .with_has_reshared(self.request.user)
            .filter(has_reshared=False)
        )

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        reshare = obj.reshare(self.request.user)

        messages.success(
            self.request, _("You have reshared this %s") % obj._meta.verbose_name,
        )

        for notification in reshare.notify_on_create():
            send_activity_notifications(obj, notification)

        return redirect(obj)


class ActivityLikeView(PermissionRequiredMixin, BaseSingleActivityView):
    permission_required = "activities.like_activity"

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            like = Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=obj.owner,
                content_object=obj,
            )
            for notification in like.notify():
                send_activity_notifications(obj, notification)

        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return redirect(obj)


class ActivityDislikeView(BaseSingleActivityView):
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.get_likes().filter(user=request.user).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return redirect(obj)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class ActivityFlagView(
    PermissionRequiredMixin, BreadcrumbsMixin, ActivityQuerySetMixin, FormView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"
    permission_required = "activities.flag_activity"

    @cached_property
    def activity(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.activity

    def get_breadcrumbs(self):
        return get_breadcrumbs_for_instance(self.activity) + [(None, _("Flag"))]

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.activity
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        for notification in flag.notify():
            send_activity_notifications(self.activity, notification)

        messages.success(
            self.request,
            _(
                "This %s has been flagged to the moderators"
                % self.activity._meta.verbose_name
            ),
        )
        return redirect(self.activity)


activity_flag_view = ActivityFlagView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, FormView
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"

    @cached_property
    def activity(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_permission_object(self):
        return self.activity

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.content_object = self.activity
        comment.community = self.request.community
        comment.owner = self.request.user
        comment.save()
        for notification in comment.notify_on_create():
            send_comment_notifications(comment, notification)
        messages.success(self.request, _("Your comment has been posted"))
        return redirect(self.activity)
