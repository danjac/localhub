# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin

from localhub.communities.views import CommunityRequiredMixin

from ..models import Invite


class InviteQuerySetMixin(CommunityRequiredMixin):
    model = Invite

    def get_queryset(self):
        return Invite.objects.for_community(self.request.community).select_related(
            "community"
        )


class InviteRecipientQuerySetMixin(LoginRequiredMixin):
    model = Invite

    def get_queryset(self):
        return (
            Invite.objects.get_queryset()
            .pending()
            .for_user(self.request.user)
            .select_related("community")
        )
