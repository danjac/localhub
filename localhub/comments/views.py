# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TemplateFormResponse, TurboFrame, redirect_303

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.common.decorators import add_messages_to_response_header
from localhub.common.mixins import SearchMixin, SuccessHeaderMixin
from localhub.common.views import ActionView
from localhub.communities.decorators import community_required
from localhub.flags.views import BaseFlagCreateView
from localhub.likes.models import Like
from localhub.users.utils import has_perm_or_403

# Local
from .forms import CommentForm
from .mixins import CommentQuerySetMixin
from .models import Comment


@community_required
def comment_detail_view(request, pk):
    qs = (
        Comment.objects.for_community(request.community)
        .with_common_annotations(request.user, request.community)
        .exclude_deleted(request.user)
        .with_common_related()
    )

    comment = get_object_or_404(qs, pk=pk)

    if request.user.is_authenticated:
        comment.get_notifications().for_recipient(request.user).unread().update(
            is_read=True
        )

    context = {"comment": comment, "content_object": comment.get_content_object()}

    if request.user.has_perm("communities.moderate_community", request.community):

        context["flags"] = (
            comment.get_flags()
            .select_related("user", "community")
            .prefetch_related("content_object")
            .order_by("-created")
        )

    context["replies"] = (
        Comment.objects.none()
        if comment.deleted
        else qs.filter(parent=comment).order_by("created")
    )

    return TemplateResponse(request, "comments/comment_detail.html", context)


@login_required
@community_required
@add_messages_to_response_header
def comment_update_view(request, pk):
    comment = get_object_or_404(
        Comment.objects.for_community(request.community).select_related(
            "owner", "community"
        ),
        pk=pk,
    )

    has_perm_or_403(request.user, "comments.change_comment", comment)

    form = CommentForm(
        request.POST if request.method == "POST" else None, instance=comment,
    )

    frame = TurboFrame(f"comment-{comment.id}-content")

    if request.method == "POST" and form.is_valid():

        comment = form.save(commit=False)
        comment.editor = request.user
        comment.edited = timezone.now()
        comment.save()

        comment.notify_on_update()

        messages.success(request, _("Your comment has been updated"))

        return frame.template(
            "comments/includes/content.html", {"comment": comment}
        ).response(request)

    return frame.template(
        "comments/includes/comment_form.html", {"form": form, "comment": comment}
    ).response(request)


@community_required
@login_required
def comment_reply_view(request, pk):
    parent = get_object_or_404(
        Comment.objects.for_community(request.community).select_related(
            "owner", "community", "parent"
        ),
        pk=pk,
    )

    has_perm_or_403(request.user, "comments.reply_to_comment", parent)

    form = CommentForm(request.POST if request.method == "POST" else None,)

    form.fields["content"].label = _("Reply")

    if request.method == "POST" and form.is_valid():
        reply = form.save(commit=False)
        reply.parent = parent
        reply.content_object = parent.content_object
        reply.owner = request.user
        reply.community = request.community
        reply.save()

        reply.notify_on_create()

        messages.success(request, _("You have replied to this comment"))
        return redirect_303(parent.content_object)

    return TemplateFormResponse(
        request,
        form,
        "comments/comment_form.html",
        {"content_object": parent.content_object, "parent": parent},
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


class BaseCommentActionView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessHeaderMixin, ActionView
):
    ...


class BaseCommentBookmarkView(BaseCommentActionView):
    permission_required = "comments.bookmark_comment"

    def render_to_response(self, has_bookmarked):
        if self.request.accept_turbo_stream:
            return (
                TurboFrame(f"comment-bookmark-{self.object.id}")
                .template(
                    "comments/includes/bookmark.html",
                    {"object": self.object, "has_bookmarked": has_bookmarked},
                )
                .response(self.request)
            )
        return HttpResponseRedirect(self.get_success_url())


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
        return self.render_success_message(self.render_to_response(has_bookmarked=True))


comment_bookmark_view = CommentBookmarkView.as_view()


class CommentRemoveBookmarkView(BaseCommentBookmarkView):
    success_message = _("You have removed this comment from your bookmarks")

    def post(self, request, *args, **kwargs):
        Bookmark.objects.filter(user=request.user, comment=self.object).delete()
        return self.render_success_message(
            self.render_to_response(has_bookmarked=False)
        )


comment_remove_bookmark_view = CommentRemoveBookmarkView.as_view()


class BaseCommentLikeView(BaseCommentActionView):
    permission_required = "comments.like_comment"

    def render_to_response(self, has_liked):
        if self.request.accept_turbo_stream:
            return (
                TurboFrame(f"comment-like-{self.object.id}")
                .template(
                    "comments/includes/like.html",
                    {"object": self.object, "has_liked": has_liked},
                )
                .response(self.request)
            )
        return HttpResponseRedirect(self.get_success_url())


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
        return self.render_to_response(has_liked=True)


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(BaseCommentLikeView):
    success_message = _("You have stopped liking this comment")

    def post(self, request, *args, **kwargs):
        Like.objects.filter(user=request.user, comment=self.object).delete()
        return self.render_to_response(has_liked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessHeaderMixin, DeleteView,
):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"
    success_message = _("You have deleted this comment")
    model = Comment

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

        messages.success(request, self.success_message)

        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()


class CommentFlagView(
    SuccessMessageMixin,
    PermissionRequiredMixin,
    CommentQuerySetMixin,
    BaseFlagCreateView,
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
