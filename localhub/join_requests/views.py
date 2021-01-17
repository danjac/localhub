# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import redirect_303, render_form_response

# Localhub
from localhub.common.forms import process_form
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_admin_required, community_required
from localhub.communities.models import Membership
from localhub.users.utils import has_perm_or_403

# Local
from .emails import send_acceptance_email, send_join_request_email, send_rejection_email
from .forms import JoinRequestForm
from .models import JoinRequest


@require_POST
@login_required
@community_admin_required
def join_request_accept_view(request, pk):
    join_req = get_join_request_or_404(
        request, pk, status=(JoinRequest.Status.PENDING, JoinRequest.Status.REJECTED)
    )

    if Membership.objects.filter(
        member=join_req.sender, community=request.community
    ).exists():
        messages.error(request, _("User already belongs to this community"))
        return redirect("join_requests:list")

    join_req.accept()

    Membership.objects.create(member=join_req.sender, community=request.community)

    send_acceptance_email(join_req)
    join_req.sender.notify_on_join(request.community)

    messages.success(
        request,
        _("Join request for %(sender)s has been accepted")
        % {"sender": join_req.sender.get_display_name()},
    )

    return redirect("join_requests:list")


@require_POST
@login_required
@community_admin_required
def join_request_reject_view(request, pk):
    join_req = get_join_request_or_404(request, pk)
    join_req.reject()
    send_rejection_email(join_req)
    messages.info(
        request,
        _("Join request for %(sender)s has been rejected")
        % {"sender": join_req.sender.get_display_name()},
    )

    return redirect("join_requests:list")


@login_required
@community_required(allow_non_members=True, permission="join_requests.create")
def join_request_create_view(request):
    with process_form(
        request, JoinRequestForm, user=request.user, community=request.community
    ) as (form, success):
        if success:
            join_req = form.save()
            send_join_request_email(join_req)
            messages.success(
                request, _("Your request has been sent to the community admins")
            )
            return redirect_303(
                settings.HOME_PAGE_URL
                if request.community.public
                else "community_welcome"
            )
        return render_form_response(
            request, form, "join_requests/joinrequest_form.html"
        )


@require_POST
@login_required
def join_request_delete_view(request, pk):
    join_req = get_object_or_404(JoinRequest, pk=pk)
    has_perm_or_403(request.user, "join_requests.delete", join_req)

    join_req.delete()

    if join_req.sender == request.user:
        success_message = _("Your join request for %(community)s has been deleted") % {
            "community": join_req.community.name
        }
        success_url = (
            "join_requests:sent_list"
            if JoinRequest.objects.for_sender(request.user).exists()
            else settings.HOME_PAGE_URL
        )
    else:
        success_message = _("Join request for %(sender)s has been deleted") % {
            "sender": join_req.sender.get_display_name()
        }
        success_url = "join_requests:list"

    messages.info(request, success_message)
    return redirect(success_url)


@login_required
@community_admin_required
def join_request_detail_view(request, pk):
    join_req = get_join_request_or_404(request, pk)
    return TemplateResponse(
        request, "join_requests/joinrequest_detail.html", {"object": join_req}
    )


@login_required
@community_admin_required
def join_request_list_view(request):

    join_reqs = get_join_request_queryset(request)
    total_count = join_reqs.count()

    status = request.GET.get("status")
    status_display = None

    if total_count == 0 or status not in JoinRequest.Status.values:
        status = None

    if status:
        status_display = dict(JoinRequest.Status.choices)[status]
        join_reqs = join_reqs.filter(status=status).order_by("-created")
    else:
        join_reqs = join_reqs.annotate(
            priority=Case(
                When(status=JoinRequest.Status.PENDING, then=Value(1)),
                default_value=0,
                output_field=IntegerField(),
            )
        ).order_by("priority", "-created")

    if request.search:
        join_reqs = join_reqs.search(request.search)

    return render_paginated_queryset(
        request,
        join_reqs,
        "join_requests/joinrequest_list.html",
        {
            "status": status,
            "status_display": status_display,
            "status_choices": list(JoinRequest.Status.choices),
            "total_count": total_count,
        },
    )


@login_required
def sent_join_request_list_view(request):
    """
    List of pending join requests sent by this user
    """

    return render_paginated_queryset(
        request,
        JoinRequest.objects.for_sender(request.user)
        .select_related("community")
        .order_by("-created"),
        "join_requests/sent_joinrequest_list.html",
        page_size=settings.LONG_PAGE_SIZE,
    )


def get_join_request_or_404(request, pk, *, status=None):
    return get_object_or_404(get_join_request_queryset(request, status), pk=pk)


def get_join_request_queryset(request, status=None):
    qs = JoinRequest.objects.for_community(request.community).select_related(
        "community", "sender"
    )
    if status:
        if isinstance(status, str):
            status = [status]
        status = list(status)
        qs = qs.filter(status__in=status)
    return qs
