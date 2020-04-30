# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _

from localhub.common.views import SuccessActionView
from localhub.communities.views import CommunityAdminRequiredMixin

from ..emails import send_invitation_email
from ..models import Invite
from .mixins import InviteQuerySetMixin, InviteRecipientQuerySetMixin


class BaseInviteAdminActionView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SuccessActionView
):
    ...


class BaseInviteRecipientActionView(InviteRecipientQuerySetMixin, SuccessActionView):
    ...


class InviteResendView(BaseInviteAdminActionView):
    success_url = reverse_lazy("invites:list")

    def get_queryset(self):
        return super().get_queryset().pending()

    def get_success_message(self):
        return _("Your invitation has been re-sent to %(email)s") % {
            "email": self.object.email
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.sent = timezone.now()
        self.object.save()

        send_invitation_email(self.object)
        return self.success_response()


invite_resend_view = InviteResendView.as_view()


class InviteAcceptView(BaseInviteRecipientActionView):
    """
    Handles an invite accept action.

    If user matches then a new membership instance is created for the
    community and the invite is flagged accordingly.
    """

    def get_success_url(self):
        if (
            self.object.is_accepted()
            and self.request.community == self.object.community
        ):
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("invites:received_list")

    def get_success_message(self):
        return _("You are now a member of %(community)s") % {
            "community": self.object.community.name
        }

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        self.object.accept(self.request.user)
        request.user.notify_on_join(self.object.community)

        return self.success_response()


invite_accept_view = InviteAcceptView.as_view()


class InviteRejectView(BaseInviteRecipientActionView):
    def get_success_url(self):
        if Invite.objects.pending().for_user(self.request.user).exists():
            return reverse("invites:received_list")
        return settings.LOCALHUB_HOME_PAGE_URL

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.reject()
        return self.success_response()


invite_reject_view = InviteRejectView.as_view()
