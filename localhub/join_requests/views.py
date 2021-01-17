# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, DetailView, ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from turbo_response import redirect_303, render_form_response

# Localhub
from localhub.common.forms import process_form
from localhub.common.mixins import SearchMixin
from localhub.communities.decorators import community_admin_required, community_required
from localhub.communities.mixins import CommunityAdminRequiredMixin
from localhub.communities.models import Membership

# Local
from .emails import send_acceptance_email, send_join_request_email, send_rejection_email
from .forms import JoinRequestForm
from .mixins import JoinRequestAdminMixin, JoinRequestQuerySetMixin
from .models import JoinRequest


@community_admin_required
@login_required
@require_POST
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


@community_admin_required
@login_required
@require_POST
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


@community_required(allow_non_members=True, permission="join_requests.create")
@login_required
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


class JoinRequestDeleteView(PermissionRequiredMixin, DeleteView):
    model = JoinRequest
    permission_required = "join_requests.delete"

    def get_queryset(self):
        return super().get_queryset().select_related("community", "sender")

    @cached_property
    def is_sender(self):
        return self.object.sender == self.request.user

    def get_success_url(self):
        if self.is_sender:
            if JoinRequest.objects.for_sender(self.request.user).exists():
                return reverse("join_requests:sent_list")
            return settings.HOME_PAGE_URL
        return reverse("join_requests:list")

    def get_success_message(self):
        if self.is_sender:
            return _("Your join request for %(community)s has been deleted") % {
                "community": self.object.community.name
            }
        return _("Join request for %(sender)s has been deleted") % {
            "sender": self.object.sender.get_display_name()
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


join_request_delete_view = JoinRequestDeleteView.as_view()


class JoinRequestDetailView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, DetailView
):
    model = JoinRequest


join_request_detail_view = JoinRequestDetailView.as_view()


class JoinRequestListView(
    JoinRequestQuerySetMixin, JoinRequestAdminMixin, SearchMixin, ListView
):
    paginate_by = settings.LONG_PAGE_SIZE
    model = JoinRequest

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in JoinRequest.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(JoinRequest.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_queryset(self):
        qs = super().get_queryset().select_related("community", "sender")
        if self.search_query:
            qs = qs.search(self.search_query)

        if self.status:
            qs = qs.filter(status=self.status).order_by("-created")
        else:
            qs = qs.annotate(
                priority=Case(
                    When(status=JoinRequest.Status.PENDING, then=Value(1)),
                    default_value=0,
                    output_field=IntegerField(),
                )
            ).order_by("priority", "-created")
        return qs

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(JoinRequest.Status.choices),
            },
        }


join_request_list_view = JoinRequestListView.as_view()


class SentJoinRequestListView(LoginRequiredMixin, ListView):
    """
    List of pending join requests sent by this user
    """

    model = JoinRequest
    paginate_by = settings.LONG_PAGE_SIZE
    template_name = "join_requests/sent_joinrequest_list.html"

    def get_queryset(self):
        return (
            JoinRequest.objects.pending()
            .for_sender(self.request.user)
            .select_related("community")
            .order_by("-created")
        )


sent_join_request_list_view = SentJoinRequestListView.as_view()


def get_join_request_or_404(request, pk, status=None):
    return get_object_or_404(get_join_request_queryset(request, status), pk=pk)


def get_join_request_queryset(request, status=None):
    qs = JoinRequest.objects.for_community(request.community)
    if status:
        if isinstance(status, str):
            status = [status]
        status = list(status)
        qs = qs.filter(status__in=status)
    return qs
