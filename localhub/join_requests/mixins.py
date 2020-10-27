# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.communities.mixins import (
    CommunityAdminRequiredMixin,
    CommunityRequiredMixin,
)

# Local
from .models import JoinRequest


class JoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return JoinRequest.objects.for_community(self.request.community)


class JoinRequestAdminMixin(CommunityAdminRequiredMixin):
    permission_required = "communities.manage_community"
