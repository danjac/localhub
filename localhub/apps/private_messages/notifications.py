# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.apps.notifications.adapter import Adapter, Mailer, Webpusher
from localhub.apps.notifications.decorators import register

# Local
from .models import Message


class MessageHeadersMixin:

    HEADERS = {
        "send": _("%(sender)s has sent you a message"),
        "reply": _("%(sender)s has replied to your message"),
        "follow_up": _("%(sender)s has sent you a follow-up to their message"),
    }


class MessageMailer(MessageHeadersMixin, Mailer):
    def get_subject(self):
        return self.HEADERS[self.adapter.verb] % {
            "sender": self.adapter.object.sender.get_display_name()
        }


class MessageWebpusher(MessageHeadersMixin, Webpusher):
    def get_header(self):
        return self.HEADERS[self.adapter.verb] % {
            "sender": self.adapter.object.sender.get_display_name()
        }

    def get_body(self):
        return self.adapter.object.abbreviate()


@register(Message)
class MessageAdapter(Adapter):
    ALLOWED_VERBS = ["send", "reply", "follow_up"]

    mailer_class = MessageMailer
    webpusher_class = MessageWebpusher
