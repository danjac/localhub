# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from localhub.views.success import SuccessDeleteView

from ..models import Message
from .mixins import SenderOrRecipientQuerySetMixin


class MessageDeleteView(SenderOrRecipientQuerySetMixin, SuccessDeleteView):
    """
    Does a "soft delete" which sets sender/recipient deleted flag
    accordingly.

    If both sender and recipient have soft-deleted, then the message
    is "hard" deleted.
    """

    model = Message
    success_message = _("This message has been deleted")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete(self.request.user)
        return self.success_response()

    def get_success_url(self):
        if self.request.user == self.object.recipient:
            return reverse("private_messages:inbox")
        return reverse("private_messages:outbox")


message_delete_view = MessageDeleteView.as_view()
