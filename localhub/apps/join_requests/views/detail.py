# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.views.generic import DetailView

from localhub.apps.communities.views import CommunityAdminRequiredMixin

from ..models import JoinRequest
from .mixins import JoinRequestQuerySetMixin


class JoinRequestDetailView(
    CommunityAdminRequiredMixin, JoinRequestQuerySetMixin, DetailView
):
    model = JoinRequest


join_request_detail_view = JoinRequestDetailView.as_view()
