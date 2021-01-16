# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import ListView

# Third Party Libraries
from turbo_response import TemplateFormResponse, TurboFrame, TurboStream

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.models import Comment
from localhub.comments.views import BaseCommentListView
from localhub.communities.decorators import community_required
from localhub.communities.rules import is_member
from localhub.likes.models import Like
from localhub.private_messages.models import Message

# Local
from .forms import UserForm
from .mixins import SingleUserMixin
from .utils import has_perm_or_403


class BaseUserActivityStreamView(SingleUserMixin, BaseActivityStreamView):
    ...


class BaseUserCommentListView(SingleUserMixin, BaseCommentListView):
    ...


class UserStreamView(BaseUserActivityStreamView):

    template_name = "users/detail/activities.html"

    def get_ordering(self):
        if self.is_current_user:
            return ("-created", "-published")
        return "-published"

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .exclude_blocked_tags(self.request.user)
            .filter(owner=self.user_obj)
        )
        if self.is_current_user:
            return qs.published_or_owner(self.request.user)
        return qs.published()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "num_likes": (
                    Like.objects.for_models(*get_activity_models())
                    .filter(recipient=self.user_obj, community=self.request.community)
                    .count()
                )
            },
        }


user_stream_view = UserStreamView.as_view()


class UserCommentListView(BaseUserCommentListView):
    template_name = "users/detail/comments.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.user_obj).order_by("-created")

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "num_likes": (
                    Like.objects.for_models(Comment)
                    .filter(recipient=self.user_obj, community=self.request.community)
                    .count()
                )
            },
        }


user_comment_list_view = UserCommentListView.as_view()


class UserMessageListView(LoginRequiredMixin, SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/detail/messages.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self):
        if self.is_blocked:
            return Message.objects.none()
        qs = (
            Message.objects.for_community(self.request.community)
            .common_select_related()
            .order_by("-created")
            .distinct()
        )

        if self.is_current_user:
            qs = qs.for_sender_or_recipient(self.request.user)
        else:
            qs = qs.between(self.request.user, self.user_obj)
        return qs

    def get_num_messages_sent(self):
        return self.get_queryset().filter(sender=self.request.user).count()

    def get_num_messages_received(self):
        return self.get_queryset().filter(recipient=self.request.user).count()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "sent_messages": self.get_num_messages_sent(),
                "received_messages": self.get_num_messages_received(),
            },
        }


user_message_list_view = UserMessageListView.as_view()


class UserActivityLikesView(BaseUserActivityStreamView):
    """Liked activities published by this user."""

    template_name = "users/likes/activities.html"
    ordering = ("-num_likes", "-published")

    exclude_blocking_users = True

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .with_num_likes()
            .published()
            .filter(owner=self.user_obj, num_likes__gt=0)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*get_activity_models())
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_activity_likes_view = UserActivityLikesView.as_view()


class UserCommentLikesView(BaseUserCommentListView):
    """Liked comments submitted by this user."""

    template_name = "users/likes/comments.html"

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(owner=self.user_obj, num_likes__gt=0)
            .order_by("-num_likes", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_comment_likes_view = UserCommentLikesView.as_view()


class UserActivityMentionsView(BaseUserActivityStreamView):
    """Activities where the user has an @mention (only
    published activities were user is not the owner)
    """

    template_name = "users/mentions/activities.html"

    exclude_blocking_users = True

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
        )


user_activity_mentions_view = UserActivityMentionsView.as_view()


class UserCommentMentionsView(BaseUserCommentListView):

    template_name = "users/mentions/comments.html"

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
            .order_by("-created")
        )


user_comment_mentions_view = UserCommentMentionsView.as_view()


@community_required
def member_list_view(request):

    qs = get_member_queryset(request)
    if search := request.GET.get("q", None):
        qs = qs.search(search).order_by("-rank")
    else:
        qs = qs.order_by("name", "username")
    return TemplateResponse(
        request, "users/list/members.html", {"members": qs, "search": search}
    )


@community_required
@login_required
def follower_user_list_view(request):
    return TemplateResponse(
        request,
        "users/list/following.html",
        {
            "members": get_member_queryset(request)
            .filter(following=request.user)
            .order_by("name", "username")
        },
    )


@community_required
@login_required
def following_user_list_view(request):
    return TemplateResponse(
        request,
        "users/list/following.html",
        {
            "members": get_member_queryset(request)
            .filter(followers=request.user)
            .order_by("name", "username")
        },
    )


@community_required
@login_required
def blocked_user_list_view(request):
    return TemplateResponse(
        request,
        "users/list/blocked.html",
        {
            "members": get_member_queryset(request, exclude_blocking_users=False)
            .filter(blockers=request.user)
            .order_by("name", "username")
        },
    )


@community_required
def user_autocomplete_list_view(request):
    qs = get_user_queryset(request)

    if request.user.is_authenticated:
        qs = qs.exclude(pk=request.user.pk)
    search_term = request.GET.get("q", "").strip()
    if search_term:
        qs = qs.filter(
            Q(Q(username__icontains=search_term) | Q(name__icontains=search_term))
        ).order_by("name", "username")[: settings.DEFAULT_PAGE_SIZE]
    else:
        qs = qs.none()

    return TemplateResponse(request, "users/list/autocomplete.html", {"users": qs})


@login_required
def user_update_view(request):
    form = UserForm(
        request.POST if request.method == "POST" else None, instance=request.user
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        request.user.notify_on_update()
        messages.success(request, _("Your details have been updated"))
        return redirect(request.path)
    return TemplateFormResponse(
        request,
        form,
        "users/user_form.html",
        {
            "is_community": request.community.active
            and is_member(request.user, request.community)
        },
    )


@community_required
@login_required
@require_POST
def user_follow_view(request, username, remove=False):

    user = get_user_or_404(request, username, permission="users.follow_user")
    if remove:
        request.user.following.remove(user)
        messages.info(request, _("You are no longer following this user"))
    else:
        request.user.following.add(user)
        request.user.notify_on_follow(user, request.community)
        messages.success(request, _("You are following this user"))

    is_detail = request.POST.get("is_detail", False)

    return (
        TurboFrame(f"user-{user.id}-follow")
        .template(
            "users/includes/follow.html",
            {"object": user, "is_following": not (remove), "is_detail": is_detail,},
        )
        .response(request)
    )


@community_required
@login_required
@require_POST
def user_block_view(request, username, remove=False):
    user = get_user_or_404(
        request,
        username,
        queryset=get_user_queryset(request, exclude_blocking_users=False),
        permission="users.block_user",
    )

    if remove:
        request.user.blocked.remove(user)
        messages.info(request, _("You are no longer blocking this user"))
    else:
        request.user.block_user(user)
        messages.success(request, _("You are now blocking this user"))

    return redirect(user)


@login_required
def user_delete_view(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect(settings.HOME_PAGE_URL)
    return TemplateResponse(request, "users/user_confirm_delete.html")


@login_required
@require_POST
def dismiss_notice_view(request, notice):
    request.user.dismiss_notice(notice)
    return TurboStream(f"notice-{notice}").remove.response()


@require_POST
def accept_cookies(request):
    response = TurboStream("accept-cookies").remove.response()
    response.set_cookie(
        "accept-cookies",
        value="true",
        expires=timezone.now() + datetime.timedelta(days=30),
        samesite="Lax",
    )
    return response


def get_user_or_404(request, username, *, queryset=None, permission=None):
    user = get_object_or_404(
        queryset or get_user_queryset(request), username__iexact=username
    )
    if permission:
        has_perm_or_403(request.user, permission, user)
    return user


def get_user_queryset(request, *, exclude_blocking_users=True):
    qs = get_user_model().objects.for_community(request.community)

    if exclude_blocking_users:
        qs = qs.exclude_blocking(request.user)

    return qs


def get_member_queryset(request, **kwargs):
    return (
        get_user_queryset(request, **kwargs)
        .with_is_following(request.user)
        .with_num_unread_messages(request.user, request.community)
        .with_role(request.community)
        .with_joined(request.community)
    )
