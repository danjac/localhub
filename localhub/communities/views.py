# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

# Third Party Libraries
import rules
from turbo_response import redirect_303, render_form_response

# Localhub
from localhub.common.forms import process_form
from localhub.common.pagination import render_paginated_queryset
from localhub.invites.models import Invite
from localhub.join_requests.models import JoinRequest
from localhub.users.utils import has_perm_or_403

# Local
from .decorators import community_admin_required, community_required
from .emails import send_membership_deleted_email
from .forms import CommunityForm, MembershipForm
from .models import Community, Membership


@community_required
def community_list_view(request):
    qs = Community.objects.accessible(request.user).order_by("name")
    if request.search:
        qs = qs.filter(name__icontains=request.search)

    if request.user.is_authenticated:

        communities = Community.objects.filter(
            membership__member=request.user, membership__active=True
        ).exclude(pk=request.community.id)

        users = (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=request.user.blocked.all())
        )

        flags = dict(
            communities.filter(
                membership__role__in=(
                    Membership.Role.ADMIN,
                    Membership.Role.MODERATOR,
                )
            )
            .annotate(num_flags=Count("flag", distinct=True))
            .values_list("id", "num_flags")
        )
        join_requests = dict(
            communities.filter(membership__role=Membership.Role.ADMIN)
            .annotate(
                num_join_requests=Count(
                    "joinrequest",
                    filter=Q(joinrequest__status=JoinRequest.Status.PENDING),
                    distinct=True,
                )
            )
            .values_list("id", "num_join_requests")
        )
        messages = dict(
            communities.annotate(
                num_messages=Count(
                    "message",
                    filter=Q(
                        message__recipient=request.user,
                        message__read__isnull=True,
                        message__sender__pk__in=users,
                        message__sender__membership__active=True,
                        message__sender__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            ).values_list("id", "num_messages")
        )
        notifications = dict(
            communities.annotate(
                num_notifications=Count(
                    "notification",
                    filter=Q(
                        notification__recipient=request.user,
                        notification__is_read=False,
                        notification__actor__pk__in=users,
                        notification__actor__membership__active=True,
                        notification__actor__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            ).values_list("id", "num_notifications")
        )

    else:
        flags = {}
        join_requests = {}
        messages = {}
        notifications = {}

    return render_paginated_queryset(
        request,
        qs,
        "communities/community_list.html",
        {
            "counters": {
                "flags": flags,
                "join_requests": join_requests,
                "messages": messages,
                "notifications": notifications,
            },
            "roles": dict(Membership.Role.choices),
        },
    )


@community_admin_required
@login_required
def community_update_view(request):
    with process_form(request, CommunityForm, instance=request.community) as (
        form,
        success,
    ):
        if success:
            form.save()
            messages.success(request, _("Community settings have been updated"))
            return redirect_303(request.path)
        return render_form_response(
            request,
            form,
            "communities/community_form.html",
        )


@community_required
def community_detail_view(request):
    return TemplateResponse(request, "communities/community_detail.html")


@community_required
def community_terms_view(request):
    return TemplateResponse(request, "communities/terms.html")


@community_required(allow_non_members=True)
@login_required
def community_welcome_view(request):
    """
    This is shown if the user is not a member (or is not authenticated).

    If user is already a member, redirects to home page.
    """

    if rules.test_rule("communities.is_member", request.user, request.community):
        return redirect(settings.HOME_PAGE_URL)

    join_request = JoinRequest.objects.filter(
        sender=request.user,
        community=request.community,
        status__in=(
            JoinRequest.Status.PENDING,
            JoinRequest.Status.REJECTED,
        ),
    ).first()

    return TemplateResponse(
        request,
        "communities/welcome.html",
        {
            "invite": (
                Invite.objects.pending()
                .for_user(request.user)
                .filter(community=request.community)
                .first()
            ),
            "join_request": join_request,
            "is_inactive_member": rules.test_rule(
                "communities.is_inactive_member",
                request.user,
                request.community,
            ),
        },
    )


def community_not_found_view(request):
    if request.community.active:
        return redirect(settings.HOME_PAGE_URL)
    return TemplateResponse(request, "communities/not_found.html")


@community_admin_required
@login_required
def membership_list_view(request):
    members = get_membership_queryset(request).order_by(
        "member__name", "member__username"
    )
    if request.search:
        members = members.search(request.search)
    return render_paginated_queryset(
        request,
        members,
        "communities/membership_list.html",
        page_size=settings.LONG_PAGE_SIZE,
    )


@community_required
@login_required
def membership_detail_view(request, pk):
    member = get_membership_or_404(
        request, pk, permission="communities.view_membership"
    )
    return TemplateResponse(
        request,
        "communities/membership_detail.html",
        {"membership": member, "object": member},
    )


@community_required
@login_required
def membership_update_view(request, pk):
    member = get_membership_or_404(
        request, pk, permission="communities.change_membership"
    )
    with process_form(request, MembershipForm, instance=member) as (form, success):
        if success:
            form.save()
            messages.success(request, _("Membership has been updated"))
            return redirect_303(member)
        return render_form_response(
            request, form, "communities/membership_form.html", {"membership": member}
        )


@community_required
@login_required
@require_POST
def membership_delete_view(request, pk):
    member = get_membership_or_404(
        request, pk, permission="communities.delete_membership"
    )

    member.delete()

    if member.member == request.user:
        return redirect(settings.HOME_PAGE_URL)

    else:
        send_membership_deleted_email(member.member, member.community)

        messages.success(
            request,
            _("You have deleted the membership for %(user)s")
            % {"user": member.member.username},
        )

        return redirect("communities:membership_list")


@community_required
@login_required
def membership_leave_view(request):
    """
    Allows the current user to be able to voluntarily leave a community.
    """

    member = get_object_or_404(get_membership_queryset(request), member=request.user)
    if request.method == "POST":
        member.delete()
        messages.success(
            request,
            _("You have left the community %(community)s")
            % {"community": member.community.name},
        )
        return redirect(settings.HOME_PAGE_URL)

    return TemplateResponse(request, "communities/membership_leave.html")


def get_membership_or_404(request, pk, permission=None):
    obj = get_object_or_404(get_membership_queryset(request), pk=pk)
    if permission:
        has_perm_or_403(request.user, permission, obj)
    return obj


def get_membership_queryset(request):
    return Membership.objects.filter(community=request.community).select_related(
        "community", "member"
    )
