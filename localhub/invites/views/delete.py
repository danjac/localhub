# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from vanilla import DeleteView

from localhub.communities.views.mixins import CommunityAdminRequiredMixin
from localhub.views import SuccessMixin

from ..models import Invite
from .mixins import InviteQuerySetMixin


class InviteDeleteView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SuccessMixin, DeleteView,
):
    success_url = reverse_lazy("invites:list")
    success_message = _("Invite has been deleted")
    model = Invite

    def get_permission_object(self):
        return self.request.community

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.success_response()


invite_delete_view = InviteDeleteView.as_view()
