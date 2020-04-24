# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models import F
from django.views.generic import DetailView, ListView

from localhub.views import SearchMixin

from ..models import Message
from .mixins import (
    RecipientQuerySetMixin,
    SenderOrRecipientQuerySetMixin,
    SenderQuerySetMixin,
)


class BaseMessageListView(SearchMixin, ListView):
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE


class InboxView(RecipientQuerySetMixin, BaseMessageListView):
    """
    Messages received by current user
    oere we should show the sender, timestamp...
    """

    template_name = "private_messages/inbox.html"

    def get_queryset(self):
        qs = super().get_queryset().with_has_bookmarked(self.request.user)
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by(F("read").desc(nulls_first=True), "-created")


inbox_view = InboxView.as_view()


class OutboxView(SenderQuerySetMixin, BaseMessageListView):
    """
    Messages sent by current user
    """

    template_name = "private_messages/outbox.html"

    def get_queryset(self):
        qs = super().get_queryset().with_has_bookmarked(self.request.user)
        if self.search_query:
            return qs.search(self.search_query).order_by("-rank", "-created")
        return qs.order_by("-created")


outbox_view = OutboxView.as_view()


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
