# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.invites.emails import send_invitation_email
from localhub.invites.models import Invite
from localhub.join_requests.emails import (
    send_acceptance_email,
    send_join_request_email,
    send_rejection_email,
)
from localhub.join_requests.forms import JoinRequestForm
from localhub.join_requests.models import JoinRequest
from localhub.users.emails import send_user_notification_email


class JoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return JoinRequest.objects.filter(community=self.request.community)


class SingleJoinRequestMixin(JoinRequestQuerySetMixin, SingleObjectMixin):
    ...


class MultipleJoinRequestMixin(JoinRequestQuerySetMixin, MultipleObjectMixin):
    ...


class SingleJoinRequestView(SingleJoinRequestMixin, View):
    ...


class JoinRequestListView(
    PermissionRequiredMixin, MultipleJoinRequestMixin, ListView
):
    permission_required = "communities.manage_community"
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("community", "sender")
            .order_by("created")
        )
        self.show_all = "all" in self.request.GET
        if not self.show_all:
            qs = qs.filter(status=JoinRequest.STATUS.pending)
        return qs


join_request_list_view = JoinRequestListView.as_view()


class JoinRequestCreateView(CommunityRequiredMixin, CreateView):
    model = JoinRequest
    form_class = JoinRequestForm
    success_url = settings.HOME_PAGE_URL
    allow_if_private = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {"community": self.request.community, "sender": self.request.user}
        )
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        send_join_request_email(self.object)

        messages.success(
            self.request,
            _("Your request has been sent to the community admins"),
        )

        return HttpResponseRedirect(self.get_success_url())


join_request_create_view = JoinRequestCreateView.as_view()


class JoinRequestActionView(PermissionRequiredMixin, SingleJoinRequestView):

    permission_required = "communities.manage_community"
    success_url = reverse_lazy("join_requests:list")

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        return super().get_queryset().filter(status=JoinRequest.STATUS.pending)

    def get_success_url(self):
        return self.success_url


class JoinRequestAcceptView(JoinRequestActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status = JoinRequest.STATUS.accepted
        self.object.save()

        user = self.object.get_sender()

        if user:
            _membership, created = Membership.objects.get_or_create(
                member=user, community=self.object.community
            )
            if created:
                send_acceptance_email(self.object)
                messages.success(request, _("Join request has been accepted"))
                for notification in user.notify_on_join(self.object.community):
                    send_user_notification_email(user, notification)

            else:
                messages.error(
                    request, _("User already belongs to this community")
                )
        else:
            invite, created = Invite.objects.get_or_create(
                sender=request.user,
                community=self.object.community,
                email=self.object.email,
            )
            if created:
                send_invitation_email(invite)
                messages.success(
                    self.request, _("An invite has been sent to this email")
                )

        return HttpResponseRedirect(self.get_success_url())


join_request_accept_view = JoinRequestAcceptView.as_view()


class JoinRequestRejectView(JoinRequestActionView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.status = JoinRequest.STATUS.rejected
        self.object.save()

        send_rejection_email(self.object)

        messages.info(self.request, _("Join request has been rejected"))

        return HttpResponseRedirect(self.get_success_url())


join_request_reject_view = JoinRequestRejectView.as_view()
