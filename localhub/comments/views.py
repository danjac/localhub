# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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

from localhub.bookmarks.models import Bookmark
from localhub.communities.views import CommunityRequiredMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like
from localhub.views import SearchMixin, SuccessMixin

from .forms import CommentForm
from .models import Comment


class CommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Comment.objects.for_community(self.request.community).select_related(
            "owner", "community", "parent", "parent__owner", "parent__community",
        )


class BaseCommentListView(CommentQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked_users(self.request.user)
            .exclude_deleted()
            .prefetch_related("content_object")
        )


class BaseCommentActionView(CommentQuerySetMixin, SuccessMixin, GenericModelView):
    ...


class CommentListView(SearchMixin, BaseCommentListView):

    template_name = "comments/comment_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


comment_list_view = CommentListView.as_view()


class CommentDetailView(CommentQuerySetMixin, DetailView):
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
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessMixin, UpdateView,
):
    form_class = CommentForm
    model = Comment
    permission_required = "comments.change_comment"
    success_message = _("Your comment has been updated")

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.notify_on_update()
        return self.success_response()


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessMixin, DeleteView,
):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"
    success_message = _("This comment has been deleted")

    def get_success_url(self):
        return super().get_success_url(object=self.object.content_object)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()


comment_delete_view = CommentDeleteView.as_view()


class CommentBookmarkView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.bookmark_comment"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()


comment_bookmark_view = CommentBookmarkView.as_view()


class CommentRemoveBookmarkView(BaseCommentActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Bookmark.objects.filter(user=request.user, comment=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_remove_bookmark_view = CommentRemoveBookmarkView.as_view()


class CommentLikeView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.like_comment"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            ).notify()
        except IntegrityError:
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(BaseCommentActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Like.objects.filter(user=request.user, comment=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


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
        return super().get_success_url(object=self.comment.content_object)

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
    success_message = _("You have replied to this comment")

    def get_permission_object(self):
        return self.parent

    def get_success_url(self):
        return super().get_success_url(object=self.object.content_object)

    @cached_property
    def parent(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        return data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.parent = self.parent
        self.object.content_object = self.parent.content_object
        self.object.owner = self.request.user
        self.object.community = self.request.community
        self.object.save()

        self.object.notify_on_create()

        return self.success_response()


comment_reply_view = CommentReplyView.as_view()
