# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.communities.views import CommunityRequiredMixin

from ..models import Message


class MessageQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return (
            Message.objects.for_community(community=self.request.community)
            .exclude_blocked(self.request.user)
            .common_select_related()
        )


class SenderQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_sender(self.request.user)


class RecipientQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_recipient(self.request.user)


class SenderOrRecipientQuerySetMixin(MessageQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().for_sender_or_recipient(self.request.user)
