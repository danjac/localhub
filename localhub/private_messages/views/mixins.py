# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.utils.functional import cached_property

from localhub.communities.views import CommunityRequiredMixin
from localhub.users.utils import user_display

from ..models import Message


class RecipientContextMixin:
    """
    Assumes self.recipient is previously defined in the view.
    """

    @cached_property
    def recipient_display(self):
        return user_display(self.recipient)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {"recipient": self.recipient, "recipient_display": self.recipient_display}
        )
        return data


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
