# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from rules.contrib.views import PermissionRequiredMixin

from localhub.apps.communities.views import CommunityRequiredMixin

from ..models import JoinRequest


class JoinRequestQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return JoinRequest.objects.for_community(self.request.community)


class JoinRequestAdminMixin(PermissionRequiredMixin):
    permission_required = "communities.manage_community"

    def get_permission_object(self):
        return self.request.community
