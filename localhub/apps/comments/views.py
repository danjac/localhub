# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin

# Localhub
from localhub.apps.bookmarks.models import Bookmark
from localhub.apps.communities.views import CommunityRequiredMixin
from localhub.apps.flags.views import BaseFlagCreateView
from localhub.apps.likes.models import Like
from localhub.views import (
    ParentObjectMixin,
    SearchMixin,
    SuccessActionView,
    SuccessCreateView,
    SuccessDeleteView,
    SuccessUpdateView,
)

# Local
from .forms import CommentForm
from .models import Comment


class CommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Comment.objects.for_community(self.request.community).select_related(
            "owner", "community", "parent", "parent__owner", "parent__community",
        )


class CommentUpdateView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessUpdateView,
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
    PermissionRequiredMixin, CommentQuerySetMixin, BaseFlagCreateView
):
    permission_required = "comments.flag_comment"
    success_message = _("This comment has been flagged to the moderators")

    def get_parent_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.parent


comment_flag_view = CommentFlagView.as_view()


class CommentReplyView(
    CommentQuerySetMixin, PermissionRequiredMixin, ParentObjectMixin, SuccessCreateView,
):
    permission_required = "comments.reply_to_comment"
    model = Comment
    form_class = CommentForm
    success_message = _("You have replied to this %(model)s")

    def get_permission_object(self):
        return self.parent

    def get_parent_queryset(self):
        return self.get_queryset()

    @cached_property
    def content_object(self):
        return self.parent.get_content_object()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["content"].label = _("Reply")
        return form

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
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


class BaseCommentListView(CommentQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_blocked_users(self.request.user)
            .exclude_deleted()
            .with_common_related()
        )


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
            .with_common_annotations(self.request.user, self.request.community)
            .exclude_deleted(self.request.user)
            .with_common_related()
        )

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.get_notifications().for_recipient(
            self.request.user
        ).unread().update(is_read=True)
        return response

    def get_flags(self):
        return (
            self.object.get_flags()
            .select_related("user", "community")
            .prefetch_related("content_object")
            .order_by("-created")
        )

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
        data.update(
            {
                "replies": self.get_replies(),
                "content_object": self.object.get_content_object(),
            }
        )
        return data


comment_detail_view = CommentDetailView.as_view()


class BaseCommentActionView(CommentQuerySetMixin, SuccessActionView):
    ...


class BaseCommentBookmarkView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.bookmark_comment"
    is_success_ajax_response = True
    success_template_name = "comments/includes/bookmark.html"


class CommentBookmarkView(BaseCommentBookmarkView):
    success_message = _("You have bookmarked this comment")

    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "has_bookmarked": True}


comment_bookmark_view = CommentBookmarkView.as_view()


class CommentRemoveBookmarkView(BaseCommentBookmarkView):
    success_message = _("You have removed this comment from your bookmarks")

    def post(self, request, *args, **kwargs):
        Bookmark.objects.filter(user=request.user, comment=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "has_bookmarked": False}


comment_remove_bookmark_view = CommentRemoveBookmarkView.as_view()


class BaseCommentLikeView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.like_comment"
    is_success_ajax_response = True
    success_template_name = "comments/includes/like.html"


class CommentLikeView(BaseCommentLikeView):
    success_message = _("You have liked this comment")

    def post(self, request, *args, **kwargs):
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            ).notify()
        except IntegrityError:
            pass
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "has_liked": True}


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(BaseCommentLikeView):
    success_message = _("You have stopped liking this comment")

    def post(self, request, *args, **kwargs):
        Like.objects.filter(user=request.user, comment=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "has_liked": False}


comment_dislike_view = CommentDislikeView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessDeleteView,
):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"
    success_message = _("You have deleted this comment")

    def get_success_url(self):
        obj = self.object.get_content_object()
        if obj:
            return obj.get_absolute_url()
        return reverse("comments:list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()


comment_delete_view = CommentDeleteView.as_view()
