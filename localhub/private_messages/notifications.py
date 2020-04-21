# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapter import Adapter, Mailer, Webpusher
from localhub.notifications.decorators import register

from .models import Message

HEADERS = {
    "send": _("%(sender)s has sent you a message"),
    "reply": _("%(sender)s has replied to your message"),
    "follow_up": _("%(sender)s has sent you a follow-up to their message"),
}


class MessageMailer(Mailer):
    def get_subject(self):
        return HEADERS[self.adapter.verb] % {
            "sender": self.adapter.object.sender.get_display_name()
        }


class MessageWebpusher(Webpusher):
    def get_header(self):
        return HEADERS[self.adapter.verb] % {
            "sender": self.adapter.object.sender.get_display_name()
        }

    def get_body(self):
        return self.adapter.object.abbreviate()


@register(Message)
class MessageAdapter(Adapter):
    ALLOWED_VERBS = ["send", "reply", "follow_up"]

    mailer_class = MessageMailer
    webpusher_class = MessageWebpusher
