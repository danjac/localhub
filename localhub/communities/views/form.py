# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessUpdateView

from ..forms import CommunityForm, MembershipForm
from ..models import Membership
from .mixins import (
    CommunityAdminRequiredMixin,
    CurrentCommunityMixin,
    MembershipQuerySetMixin,
)


class CommunityUpdateView(
    CurrentCommunityMixin, CommunityAdminRequiredMixin, SuccessUpdateView
):
    form_class = CommunityForm
    success_message = _("Community settings have been updated")

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.save()
        return self.success_response()


community_update_view = CommunityUpdateView.as_view()


class MembershipUpdateView(
    PermissionRequiredMixin, MembershipQuerySetMixin, SuccessUpdateView,
):
    model = Membership
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_message = _("Membership has been updated")


membership_update_view = MembershipUpdateView.as_view()
