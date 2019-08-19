# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext as _
from django.utils.translation import override

from localhub.messageboard.models import MessageRecipient
from localhub.notifications.utils import send_push_notification


def send_message_push(recipient: MessageRecipient):
    with override(recipient.recipient.language):
        send_push_notification(
            recipient.recipient,
            head=_("%(sender)s has sent you a message")
            % {"sender": recipient.message.sender},
            body=recipient.message.subject,
            url=recipient.get_permalink(),
        )
