# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _

from localhub.apps.communities.views import (
    CommunityAdminRequiredMixin,
    CommunityRequiredMixin,
)
from localhub.common.views import SuccessCreateView

from ..emails import send_invitation_email
from ..forms import InviteForm
from ..models import Invite


class InviteCreateView(
    CommunityAdminRequiredMixin, CommunityRequiredMixin, SuccessCreateView,
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"community": self.request.community})
        return kwargs

    def get_success_message(self):
        return _("Your invitation has been sent to %(email)s") % {
            "email": self.object.email
        }

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.sender = self.request.user
        self.object.community = self.request.community
        self.object.sent = timezone.now()
        self.object.save()

        # send email to recipient
        send_invitation_email(self.object)
        return self.success_response()


invite_create_view = InviteCreateView.as_view()
