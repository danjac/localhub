
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from vanilla import CreateView

from localhub.communities.views import CommunityRequiredMixin
from localhub.views import SuccessMixin

from ..emails import send_invitation_email
from ..forms import InviteForm
from ..models import Invite

from .mixins import InviteAdminMixin


class InviteCreateView(
    InviteAdminMixin, CommunityRequiredMixin, SuccessMixin, CreateView,
):
    model = Invite
    form_class = InviteForm
    success_url = reverse_lazy("invites:list")

    def get_form(self, data=None, files=None):
        return self.form_class(self.request.community, data, files)

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
