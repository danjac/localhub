# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from vanilla import DetailView

from ..models import Message
from .mixins import SenderOrRecipientQuerySetMixin


class MessageDetailView(SenderOrRecipientQuerySetMixin, DetailView):

    model = Message

    def get_queryset(self):
        return super().get_queryset().with_has_bookmarked(self.request.user)

    def get_object(self):
        obj = super().get_object()
        if obj.recipient == self.request.user:
            obj.mark_read(mark_replies=True)
        return obj

    def get_replies(self):
        return (
            self.object.get_all_replies()
            .for_sender_or_recipient(self.request.user)
            .common_select_related()
            .order_by("created")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "replies": self.get_replies(),
                "parent": self.object.get_parent(self.request.user),
                "other_user": self.object.get_other_user(self.request.user),
            }
        )

        return data


message_detail_view = MessageDetailView.as_view()
