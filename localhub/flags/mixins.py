# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.communities.mixins import CommunityModeratorRequiredMixin

# Local
from .models import Flag


class FlagQuerySetMixin(CommunityModeratorRequiredMixin):
    def get_queryset(self):
        return Flag.objects.filter(community=self.request.community)
