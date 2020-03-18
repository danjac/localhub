# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
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

from localhub.activities.utils import get_breadcrumbs_for_instance
from localhub.communities.views import CommunityRequiredMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like
from localhub.views import BreadcrumbsMixin, SearchMixin

from .forms import CommentForm
from .models import Comment


class CommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Comment.objects.for_community(self.request.community).select_related(
            "owner", "community", "parent", "parent__owner", "parent__community",
        )


class BaseCommentListView(CommentQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked_users(self.request.user)
            .exclude_deleted()
            .prefetch_related("content_object")
        )


class CommentListView(SearchMixin, BaseCommentListView):
    template_name = "comments/comment_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


comment_list_view = CommentListView.as_view()


class CommentDetailView(CommentQuerySetMixin, BreadcrumbsMixin, DetailView):
    model = Comment

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude_deleted(self.request.user)
            .select_related("editor")
            .with_common_annotations(self.request.user, self.request.community)
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_breadcrumbs(self):
        if self.object.content_object:
            return get_breadcrumbs_for_instance(self.object.content_object) + [
                (None, _("Comment"))
            ]
        return []

    def get_flags(self):
        return self.object.get_flags().select_related("user").order_by("-created")

    def get_replies(self):
        if self.object.deleted:
            return self.get_queryset().none()
        return self.get_queryset().filter(parent=self.object).order_by("created")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()
        data["replies"] = self.get_replies()
        return data


comment_detail_view = CommentDetailView.as_view()


class CommentUpdateView(
    PermissionRequiredMixin, CommentQuerySetMixin, BreadcrumbsMixin, UpdateView
):
    form_class = CommentForm
    model = Comment
    permission_required = "comments.change_comment"

    def get_breadcrumbs(self):
        breadcrumbs = [
            (self.object.get_absolute_url(), _("Comment")),
            (None, _("Edit")),
        ]
        if self.object.content_object:
            breadcrumbs = (
                get_breadcrumbs_for_instance(self.object.content_object) + breadcrumbs
            )

        return breadcrumbs

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.editor = self.request.user
        comment.edited = timezone.now()
        comment.save()

        comment.notify_on_update()

        messages.success(self.request, _("Comment has been updated"))
        return redirect(comment.content_object)


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(PermissionRequiredMixin, CommentQuerySetMixin, DeleteView):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if self.request.user != comment.owner:
            comment.soft_delete()
            comment.notify_on_delete(self.request.user)
        else:
            comment.delete()

        messages.success(request, _("Comment has been deleted"))
        return redirect(comment.content_object)


comment_delete_view = CommentDeleteView.as_view()


class CommentLikeView(
    PermissionRequiredMixin, CommentQuerySetMixin, GenericModelView,
):
    permission_required = "comments.like_comment"

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=comment.owner,
                content_object=comment,
            ).notify()
        except IntegrityError:
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return redirect(comment)


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(CommentQuerySetMixin, GenericModelView):
    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        Like.objects.filter(user=request.user, comment=comment).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return redirect(comment)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


class CommentFlagView(
    PermissionRequiredMixin, BreadcrumbsMixin, CommentQuerySetMixin, FormView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"
    permission_required = "comments.flag_comment"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.comment

    @cached_property
    def comment(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_breadcrumbs(self):
        breadcrumbs = [
            (self.comment.get_absolute_url(), _("Comment")),
            (None, _("Flag")),
        ]
        if self.comment.content_object:
            breadcrumbs = (
                get_breadcrumbs_for_instance(self.comment.content_object) + breadcrumbs
            )
        return breadcrumbs

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.comment
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        flag.notify()

        messages.success(
            self.request, _("This comment has been flagged to the moderators")
        )
        return redirect(self.comment.content_object)


comment_flag_view = CommentFlagView.as_view()


class CommentReplyView(
    CommentQuerySetMixin, BreadcrumbsMixin, PermissionRequiredMixin, CreateView,
):
    permission_required = "comments.reply_to_comment"
    model = Comment
    form_class = CommentForm

    def get_permission_object(self):
        return self.parent

    def get_breadcrumbs(self):
        breadcrumbs = [
            (self.parent.get_absolute_url(), _("Parent")),
            (None, _("Reply")),
        ]
        if self.parent.content_object:
            breadcrumbs = (
                get_breadcrumbs_for_instance(self.parent.content_object) + breadcrumbs
            )
        return breadcrumbs

    @cached_property
    def parent(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        return data

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.parent = self.parent
        comment.content_object = self.parent.content_object
        comment.owner = self.request.user
        comment.community = self.request.community
        comment.save()

        comment.notify_on_create()
        messages.success(self.request, _("Your comment has been posted"))
        return redirect(comment.content_object)


comment_reply_view = CommentReplyView.as_view()
