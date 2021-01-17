# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import http

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import redirect_303, render_form_response

# Localhub
from localhub.common.decorators import add_messages_to_response_header
from localhub.common.forms import process_form
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_admin_required

# Local
from .emails import send_invitation_email
from .forms import InviteForm
from .models import Invite


@require_POST
@login_required
@community_admin_required
@add_messages_to_response_header
def invite_resend_view(request, pk):
    invite = get_invite_or_404(request, pk)
    invite.sent = timezone.now()
    invite.save()

    send_invitation_email(invite)
    messages.success(
        request,
        _("Your invitation has been re-sent to %(email)s") % {"email": invite.email},
    )

    return HttpResponse(status=http.HTTPStatus.NO_CONTENT)


@login_required
@require_POST
def invite_accept_view(request, pk):
    """
    Handles an invite accept action.

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    invite = get_recipient_invite_or_404(request, pk)
    invite.accept(request.user)
    request.user.notify_on_join(invite.community)

    messages.success(
        request,
        _("You are now a member of %(community)s")
        % {"community": invite.community.name},
    )

    return redirect(
        settings.HOME_PAGE_URL
        if invite.is_accepted() and request.community == invite.community
        else "invites:received_list"
    )


@require_POST
@login_required
def invite_reject_view(request, pk):
    invite = get_recipient_invite_or_404(request, pk)
    invite.reject()

    return redirect(
        "invites:received_list"
        if Invite.objects.pending().for_user(request.user).exists()
        else settings.HOME_PAGE_URL
    )


@login_required
@community_admin_required
def invite_create_view(request):

    with process_form(request, InviteForm, community=request.community) as (
        form,
        success,
    ):
        if success:

            invite = form.save(commit=False)
            invite.sender = request.user
            invite.community = request.community
            invite.sent = timezone.now()
            invite.save()

            # send email to recipient
            send_invitation_email(invite)

            messages.success(
                request,
                _("Your invitation has been sent to %(email)s")
                % {"email": invite.email},
            )
            return redirect_303("invites:list")

        return render_form_response(request, form, "invites/invite_form.html")


@require_POST
@login_required
@community_admin_required
def invite_delete_view(request, pk):
    invite = get_invite_or_404(request, pk)
    invite.delete()
    messages.info(request, _("You have deleted this invite"))
    return redirect("invites:list")


@login_required
def invite_detail_view(request, pk):
    invite = get_recipient_invite_or_404(request, pk)
    return TemplateResponse(request, "invites/invite_detail.html", {"invite": invite})


@login_required
@community_admin_required
def invite_list_view(request):
    invites = get_invite_queryset(request).order_by("-created")
    total_count = invites.count()

    status = request.GET.get("status")
    status_display = None

    if total_count == 0 or status not in Invite.Status.values:
        status = None
    if status:
        status_display = dict(Invite.Status.choices)[status]
        invites = invites.filter(status=status)

    if request.search:
        invites = invites.filter(email__icontains=request.search)

    return render_paginated_queryset(
        request,
        invites,
        "invites/invite_list.html",
        {
            "status": status,
            "status_display": status_display,
            "status_choices": list(Invite.Status.choices),
            "total_count": total_count,
        },
        page_size=settings.LONG_PAGE_SIZE,
    )


@login_required
def received_invite_list_view(request):
    invites = get_recipient_invite_queryset(request).order_by("-created")
    return render_paginated_queryset(
        request,
        invites,
        "invites/received_invite_list.html",
        page_size=settings.LONG_PAGE_SIZE,
    )


def get_invite_or_404(request, pk):
    return get_object_or_404(get_invite_queryset(request), pk=pk)


def get_recipient_invite_or_404(request, pk):
    return get_object_or_404(get_recipient_invite_queryset(request), pk=pk)


def get_invite_queryset(request):
    return Invite.objects.for_community(request.community).select_related("community")


def get_recipient_invite_queryset(request):
    return Invite.objects.pending().for_user(request.user).select_related("community")
