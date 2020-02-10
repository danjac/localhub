# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import (
    CreateView,
    DeleteView,
    DetailView,
    GenericModelView,
    ListView,
)

from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.users.notifications import send_user_notification
from localhub.users.utils import user_display
from localhub.views import BreadcrumbsMixin, SearchMixin

from .emails import (
    send_acceptance_email,
    send_join_request_email,
    send_rejection_email,
)
from .forms import JoinRequestForm
from .models import JoinRequest


class JoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return JoinRequest.objects.filter(community=self.request.community)


class JoinRequestManageMixin(PermissionRequiredMixin, JoinRequestQuerySetMixin):
    permission_required = "communities.manage_community"

    def get_permission_object(self):
        return self.request.community


class JoinRequestListView(JoinRequestManageMixin, SearchMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    model = JoinRequest

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in JoinRequest.STATUS and self.total_count:
            return status
        return None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_queryset(self):
        qs = super().get_queryset().select_related("community", "sender")
        if self.search_query:
            qs = qs.search(self.search_query)

        if self.status:
            qs = (
                qs.filter(status=self.status)
                .annotate(
                    priority=Case(
                        When(status=JoinRequest.STATUS.pending, then=Value(1)),
                        default_value=0,
                        output_field=IntegerField(),
                    )
                )
                .order_by("priority", "-created")
            )
        else:
            qs = qs.order_by("-created")
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "total_count": self.total_count,
                "status": self.status,
                "status_choices": list(JoinRequest.STATUS),
            }
        )
        return data


join_request_list_view = JoinRequestListView.as_view()


class JoinRequestDetailView(JoinRequestManageMixin, BreadcrumbsMixin, DetailView):
    model = JoinRequest

    def get_breadcrumbs(self):
        return [
            (reverse("join_requests:list"), _("Join Requests")),
            (None, user_display(self.object.sender)),
        ]


join_request_detail_view = JoinRequestDetailView.as_view()


class JoinRequestDeleteView(JoinRequestManageMixin, DeleteView):
    model = JoinRequest
    success_url = reverse_lazy("join_requests:list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        messages.success(
            request,
            _("Join request for %(sender)s has been deleted")
            % {"sender": user_display(self.object.sender)},
        )

        return redirect(self.get_success_url())


join_request_delete_view = JoinRequestDeleteView.as_view()


class JoinRequestActionView(JoinRequestManageMixin, GenericModelView):
    success_url = reverse_lazy("join_requests:list")

    def get_queryset(self):
        return super().get_queryset().filter(status=JoinRequest.STATUS.pending)

    def get_success_url(self):
        return self.success_url


class JoinRequestAcceptView(JoinRequestActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = JoinRequest.STATUS.accepted
        self.object.save()

        _membership, created = Membership.objects.get_or_create(
            member=self.object.sender, community=self.object.community
        )
        if created:
            send_acceptance_email(self.object)
            messages.success(
                request,
                _("Join request for %(sender)s has been accepted")
                % {"sender": user_display(self.object.sender)},
            )
            for notification in self.object.sender.notify_on_join(
                self.object.community
            ):
                send_user_notification(self.object.sender, notification)

        else:
            messages.error(request, _("User already belongs to this community"))

        return HttpResponseRedirect(self.get_success_url())


join_request_accept_view = JoinRequestAcceptView.as_view()


class JoinRequestRejectView(JoinRequestActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.status = JoinRequest.STATUS.rejected
        self.object.save()

        send_rejection_email(self.object)

        messages.info(
            request,
            _("Join request for %(sender)s has been rejected")
            % {"sender": user_display(self.object.sender)},
        )

        return HttpResponseRedirect(self.get_success_url())


join_request_reject_view = JoinRequestRejectView.as_view()


class JoinRequestCreateView(
    PermissionRequiredMixin, CommunityRequiredMixin, CreateView
):
    model = JoinRequest
    form_class = JoinRequestForm
    template_name = "join_requests/joinrequest_form.html"
    allow_non_members = True
    permission_required = "join_requests.create"

    def get_permission_object(self):
        return self.request.community

    def get_form(self, *args, **kwargs):
        return self.get_form_class()(
            self.request.user, self.request.community, *args, **kwargs
        )

    def form_valid(self, form):

        join_request = form.save()

        send_join_request_email(join_request)

        messages.success(
            self.request, _("Your request has been sent to the community admins"),
        )

        return redirect("community_welcome")


join_request_create_view = JoinRequestCreateView.as_view()
