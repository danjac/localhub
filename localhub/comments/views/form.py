# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import CreateView, FormView, UpdateView

from localhub.flags.forms import FlagForm
from localhub.views import SuccessMixin

from ..forms import CommentForm
from ..models import Comment
from .mixins import CommentQuerySetMixin


class CommentUpdateView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessMixin, UpdateView,
):
    form_class = CommentForm
    model = Comment
    permission_required = "comments.change_comment"
    success_message = _("Your %(model)s has been updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_object"] = self.object.get_content_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.notify_on_update()
        return self.success_response()


comment_update_view = CommentUpdateView.as_view()


class CommentFlagView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessMixin, FormView,
):
    form_class = FlagForm
    template_name = "comments/flag_form.html"
    permission_required = "comments.flag_comment"
    success_message = _("This comment has been flagged to the moderators")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.comment

    def get_success_url(self):
        return super().get_success_url(object=self.comment)

    @cached_property
    def comment(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["comment"] = self.comment
        return data

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.comment
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        flag.notify()

        return self.success_response()


comment_flag_view = CommentFlagView.as_view()


class CommentReplyView(
    CommentQuerySetMixin, PermissionRequiredMixin, SuccessMixin, CreateView,
):
    permission_required = "comments.reply_to_comment"
    model = Comment
    form_class = CommentForm
    success_message = _("You have replied to this %(model)s")

    def get_permission_object(self):
        return self.parent

    @cached_property
    def parent(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    @cached_property
    def content_object(self):
        return self.parent.get_content_object()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        data["content_object"] = self.content_object
        return data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.parent = self.parent
        self.object.content_object = self.content_object
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        self.object.notify_on_create()

        return self.success_response()


comment_reply_view = CommentReplyView.as_view()
