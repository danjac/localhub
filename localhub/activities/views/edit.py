# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.comments.forms import CommentForm
from localhub.communities.views import CommunityRequiredMixin
from localhub.flags.forms import FlagForm
from localhub.views import (
    ParentObjectMixin,
    SuccessCreateView,
    SuccessFormView,
    SuccessUpdateView,
)

from ..forms import ActivityTagsForm
from .mixins import ActivityQuerySetMixin, ActivityTemplateMixin


class ActivityCreateView(
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    ActivityTemplateMixin,
    SuccessCreateView,
):
    permission_required = "activities.create_activity"

    def get_permission_object(self):
        return self.request.community

    def get_success_message(self):
        return super().get_success_message(
            _("Your %(model)s has been published")
            if self.object.published
            else _("Your %(model)s has been saved to your Private Stash")
        )

    def form_valid(self, form):

        publish = "save_private" not in self.request.POST

        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.community = self.request.community

        if publish:
            self.object.published = timezone.now()

        self.object.save()

        if publish:
            self.object.notify_on_create()

        return self.success_response()


class ActivityUpdateView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessUpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been updated")

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.update_reshares()

        if self.object.published:
            self.object.notify_on_update()

        return self.success_response()


class ActivityUpdateTagsView(ActivityUpdateView):
    """
    Allows a moderator to update the tags on a view, e.g
    to add a "content sensitive" tag.
    """

    form_class = ActivityTagsForm
    permission_required = "activities.change_activity_tags"
    success_message = _("Tags have been updated")

    def get_queryset(self):
        return super().get_queryset().published()


class ActivityFlagView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ParentObjectMixin, SuccessFormView,
):
    form_class = FlagForm
    template_name = "activities/flag_form.html"
    permission_required = "activities.flag_activity"
    success_message = _("This %(model)s has been flagged to the moderators")

    parent_object_name = "activity"

    def get_parent_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            activity=self.activity, activity_model=self.activity.__class__, **kwargs
        )

    def get_permission_object(self):
        return self.activity

    def get_success_url(self):
        return super().get_success_url(object=self.activity)

    def get_success_message(self):
        return super().get_success_message(model=self.activity)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.activity
        self.object.community = self.request.community
        self.object.user = self.request.user
        self.object.save()

        self.object.notify()

        return self.success_response()


activity_flag_view = ActivityFlagView.as_view()


class ActivityCommentCreateView(
    PermissionRequiredMixin, ActivityQuerySetMixin, ParentObjectMixin, SuccessFormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "activities.create_comment"
    success_message = _("Your %(model)s has been posted")

    parent_object_name = "content_object"

    def get_permission_object(self):
        return self.content_object

    def get_parent_queryset(self):
        return self.get_queryset()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.content_object = self.content_object
        self.object.community = self.request.community
        self.object.owner = self.request.user
        self.object.save()

        self.object.notify_on_create()

        return self.success_response()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {"content_object_model": self.content_object.__class__,}
        )
        return data
