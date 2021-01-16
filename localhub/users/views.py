# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import datetime

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import TemplateFormResponse, TurboFrame, TurboStream

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import render_activity_stream
from localhub.comments.models import Comment
from localhub.comments.views import get_comment_queryset
from localhub.common.pagination import get_pagination_context, render_paginated_queryset
from localhub.communities.decorators import community_required
from localhub.communities.models import Membership
from localhub.communities.rules import is_member
from localhub.likes.models import Like
from localhub.private_messages.models import Message

# Local
from .forms import UserForm
from .utils import has_perm_or_403


@community_required
def user_stream_view(request, username):
    user = get_user_or_404(request, username)

    is_current_user = user == request.user

    if request.user.is_authenticated and not is_current_user:
        user.get_notifications().for_recipient(request.user).unread().update(
            is_read=True
        )

    def _filter_queryset(qs):
        qs = qs.exclude_blocked_tags(request.user).filter(owner=user)
        if is_current_user:
            return qs.published_or_owner(request.user)
        return qs.published()

    num_likes = (
        Like.objects.for_models(*get_activity_models())
        .filter(recipient=user, community=request.community)
        .count()
    )

    return render_activity_stream(
        request,
        _filter_queryset,
        "users/detail/activities.html",
        ordering=("-created", "-published") if is_current_user else "-published",
        extra_context={
            **get_user_detail_context(request, user),
            "num_likes": num_likes,
        },
    )


@community_required
@login_required
def user_message_list_view(request, username):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    user = get_user_or_404(request, username)
    messages = (
        Message.objects.for_community(request.community)
        .common_select_related()
        .order_by("-created")
        .distinct()
    )

    if user == request.user:
        messages = messages.for_sender_or_recipient(request.user)
    else:
        messages = messages.between(request.user, user)

    sent_messages = messages.filter(sender=request.user).count()
    received_messages = messages.filter(recipient=request.user).count()

    return render_user_detail(
        request,
        user,
        "users/detail/messages.html",
        {
            "sent_messages": sent_messages,
            "received_messages": received_messages,
            **get_pagination_context(request, messages),
        },
    )


@community_required
def user_activity_likes_view(request, username):
    """Liked activities published by this user."""
    user = get_user_or_404(request, username)
    num_likes = (
        Like.objects.for_models(*get_activity_models())
        .filter(recipient=user, community=request.community)
        .count()
    )

    return render_activity_stream(
        request,
        lambda qs: qs.with_num_likes().published().filter(owner=user, num_likes__gt=0),
        "users/likes/activities.html",
        ordering=("-num_likes", "-published"),
        extra_context={
            **get_user_detail_context(request, user),
            "num_likes": num_likes,
        },
    )


@community_required
def user_comment_likes_view(request, username):
    """Liked comments submitted by this user."""
    user = get_user_or_404(request, username)

    comments = (
        get_comment_queryset(request)
        .filter(owner=user, num_likes__gt=0)
        .order_by("-num_likes", "-created")
    )

    num_likes = (
        Like.objects.for_models(Comment)
        .filter(recipient=user, community=request.community)
        .count()
    )

    return render_user_detail(
        request,
        user,
        "users/likes/comments.html",
        {"num_likes": num_likes, **get_pagination_context(request, comments)},
    )


@community_required
def user_comment_list_view(request, username):
    user = get_user_or_404(request, username)
    comments = get_comment_queryset(request).filter(owner=user).order_by("-created")

    num_likes = (
        Like.objects.for_models(Comment)
        .filter(recipient=user, community=request.community)
        .count()
    )

    return render_user_detail(
        request,
        user,
        "users/detail/comments.html",
        {"num_likes": num_likes, **get_pagination_context(request, comments)},
    )


@community_required
def user_comment_mentions_view(request, username):
    user = get_user_or_404(request, username)
    comments = (
        get_comment_queryset(request)
        .exclude(owner=user)
        .search(f"@{user.username}")
        .order_by("-created")
    )
    return render_user_detail(
        request,
        user,
        "users/mentions/comments.html",
        get_pagination_context(request, comments),
    )


@community_required
def user_activity_mentions_view(request, username):
    """Activities where the user has an @mention (only
    published activities were user is not the owner)
    """
    user = get_user_or_404(request, username)

    return render_activity_stream(
        request,
        lambda qs: qs.published().exclude(owner=user).search(f"@{user.username}"),
        "users/mentions/activities.html",
        ordering="-published",
        extra_context=get_user_detail_context(request, user),
    )


@community_required
def member_list_view(request):

    qs = get_member_queryset(request)
    if search := request.GET.get("q", None):
        qs = qs.search(search).order_by("-rank")
    else:
        qs = qs.order_by("name", "username")

    return render_paginated_queryset(
        request, qs, "users/list/members.html", {"search": search}
    )


@community_required
@login_required
def follower_user_list_view(request):
    return render_paginated_queryset(
        request,
        get_member_queryset(request)
        .filter(following=request.user)
        .order_by("name", "username"),
        "users/list/following.html",
    )


@community_required
@login_required
def following_user_list_view(request):
    return render_paginated_queryset(
        request,
        get_member_queryset(request)
        .filter(followers=request.user)
        .order_by("name", "username"),
        "users/list/following.html",
    )


@community_required
@login_required
def blocked_user_list_view(request):
    return render_paginated_queryset(
        request,
        get_member_queryset(request, exclude_blocking_users=False)
        .filter(blockers=request.user)
        .order_by("name", "username"),
        "users/list/blocked.html",
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
    try:
        queryset = queryset or get_user_queryset(request)
        user = queryset.get(username__iexact=username)
    except ObjectDoesNotExist:
        raise Http404(
            render_to_string(
                "users/detail/not_found.html", {"username": username}, request=request
            )
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


def get_user_detail_context(request, user):
    is_current_user = user == request.user

    if request.user.is_authenticated and not is_current_user:
        is_blocker = request.user.blockers.filter(pk=user.id).exists()
        is_blocking = request.user.blocked.filter(pk=user.id).exists()
        is_follower = request.user.followers.filter(pk=user.id).exists()
        is_following = request.user.following.filter(pk=user.id).exists()

        unread_messages = (
            Message.objects.for_community(request.community)
            .from_sender_to_recipient(user, request.user)
            .unread()
            .count()
        )

    else:
        is_blocker = False
        is_blocking = False
        is_follower = False
        is_following = False
        unread_messages = 0

    membership = Membership.objects.filter(
        member=user, community=request.community
    ).first()

    return {
        "display_name": user.get_display_name(),
        "is_blocker": is_blocker,
        "is_blocking": is_blocking,
        "is_current_user": is_current_user,
        "is_follower": is_follower,
        "is_following": is_following,
        "membership": membership,
        "unread_messages": unread_messages,
        "user_obj": user,
    }


def render_user_detail(request, user, template_name, extra_context=None):
    return TemplateResponse(
        request,
        template_name,
        {**get_user_detail_context(request, user), **(extra_context or {})},
    )
