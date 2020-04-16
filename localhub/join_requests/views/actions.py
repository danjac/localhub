# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from localhub.communities.models import Membership
from localhub.communities.views import CommunityAdminRequiredMixin
from localhub.views import BaseActionView

from ..emails import send_acceptance_email, send_rejection_email
from ..models import JoinRequest
from .mixins import JoinRequestQuerySetMixin


class BaseJoinRequestActionView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, BaseActionView
):
    success_url = reverse_lazy("join_requests:list")


class JoinRequestAcceptView(BaseJoinRequestActionView):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                status__in=(JoinRequest.Status.PENDING, JoinRequest.Status.REJECTED)
            )
        )

    def get_success_message(self):
        return _("Join request for %(sender)s has been accepted") % {
            "sender": self.object.sender.get_display_name()
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if Membership.objects.filter(
            member=self.object.sender, community=self.object.community
        ).exists():
            messages.error(request, _("User already belongs to this community"))
            return HttpResponseRedirect(reverse("join_requests:list"))

        self.object.accept()

        Membership.objects.create(
            member=self.object.sender, community=self.object.community
        )

        send_acceptance_email(self.object)

        self.object.sender.notify_on_join(self.object.community)

        return self.success_response()


join_request_accept_view = JoinRequestAcceptView.as_view()


class JoinRequestRejectView(BaseJoinRequestActionView):
    def get_queryset(self):
        return super().get_queryset().pending()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.reject()

        send_rejection_email(self.object)

        messages.info(
            request,
            _("Join request for %(sender)s has been rejected")
            % {"sender": self.object.sender.get_display_name()},
        )

        return self.success_response()


join_request_reject_view = JoinRequestRejectView.as_view()
