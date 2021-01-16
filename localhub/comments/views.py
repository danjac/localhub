# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import TemplateFormResponse, TurboFrame, redirect_303

# Localhub
from localhub.bookmarks.models import Bookmark
from localhub.common.decorators import add_messages_to_response_header
from localhub.communities.decorators import community_required
from localhub.flags.views import BaseFlagCreateView
from localhub.likes.models import Like
from localhub.users.utils import has_perm_or_403

# Local
from .forms import CommentForm
from .mixins import CommentQuerySetMixin
from .models import Comment


@community_required
def comment_list_view(request):
    comments = (
        Comment.objects.for_community(request.community)
        .with_common_annotations(request.user, request.community)
        .exclude_blocked_users(request.user)
        .exclude_deleted()
        .with_common_related()
    )

    if search := request.GET.get("q", None):
        comments = comments.search(search).order_by("-rank", "-created")
    else:
        comments = comments.order_by("-created")

    return TemplateResponse(
        request,
        "comments/comment_list.html",
        {"comments": comments, "search": search,},
    )


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
    comment = get_comment_or_404(request, pk, permission="comments.change_comment")

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
    parent = get_comment_or_404(request, pk, permission="comments.reply_to_comment")

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


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def comment_bookmark_view(request, pk, remove=False):
    comment = get_comment_or_404(request, pk, permission="comments.bookmark_comment")
    if remove:
        Bookmark.objects.filter(user=request.user, comment=comment).delete()
        messages.info(request, _("You have removed this bookmark"))
    else:
        try:
            Bookmark.objects.create(
                user=request.user, community=request.community, content_object=comment,
            )
            messages.success(request, _("You have bookmarked this comment"))
        except IntegrityError:
            pass

    if request.accept_turbo_stream:
        return (
            TurboFrame(f"comment-bookmark-{comment.id}")
            .template(
                "comments/includes/bookmark.html",
                {"object": comment, "has_bookmarked": not (remove)},
            )
            .response(request)
        )
    return redirect(comment)


@community_required
@login_required
@add_messages_to_response_header
@require_POST
def comment_like_view(request, pk, remove=False):
    comment = get_comment_or_404(request, pk, permission="comments.like_comment")

    if remove:
        Like.objects.filter(user=request.user, comment=comment).delete()
        messages.info(request, _("You have stopped liking this comment"))
    else:

        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=comment.owner,
                content_object=comment,
            ).notify()

            messages.success(request, _("You have liked this comment"))

        except IntegrityError:
            pass

    if request.accept_turbo_stream:
        return (
            TurboFrame(f"comment-like-{comment.id}")
            .template(
                "comments/includes/like.html",
                {"object": comment, "has_liked": not (remove)},
            )
            .response(request)
        )
    return redirect(comment)


@community_required
@login_required
@require_POST
def comment_delete_view(request, pk):
    comment = get_comment_or_404(request, pk, permission="comments.delete_comment")

    if request.user == comment.owner:
        comment.delete()
    else:
        comment.soft_delete()
        comment.notify_on_delete(request.user)

    messages.info(request, _("You have deleted this comment"))

    return redirect(comment.get_content_object() or "comments:list")


def get_comment_or_404(request, pk, *, permission=None):

    comment = get_object_or_404(
        Comment.objects.for_community(request.community).select_related(
            "owner", "community"
        ),
        pk=pk,
    )

    if permission:
        has_perm_or_403(request.user, permission, comment)
    return comment


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
