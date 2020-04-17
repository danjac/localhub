# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from localhub.communities.views.mixins import CommunityAdminRequiredMixin
from localhub.views import SuccessDeleteView

from ..models import Invite
from .mixins import InviteQuerySetMixin


class InviteDeleteView(
    CommunityAdminRequiredMixin, InviteQuerySetMixin, SuccessDeleteView,
):
    success_url = reverse_lazy("invites:list")
    success_message = _("You have deleted this invite")
    model = Invite


invite_delete_view = InviteDeleteView.as_view()
