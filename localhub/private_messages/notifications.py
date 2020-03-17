# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext as _

from localhub.notifications.adapters import (
    BaseAdapter,
    Mailer,
    Webpusher,
)
from localhub.notifications.decorators import register
from localhub.users.utils import user_display

from .models import Message


class MessageMailer(Mailer):
    def get_subject(self):
        if self.object.parent:
            subject = _("%(sender)s has replied to your message")
        else:
            subject = _("%(sender)s has sent you a message")
        return subject % {"sender": user_display(self.object.sender)}


class MessageWebpusher(Webpusher):
    def get_header(self):
        if self.object.parent:
            subject = _("%(sender)s has replied to your message")
        else:
            subject = _("%(sender)s has sent you a message")
        return subject % {"sender": user_display(self.object.sender)}

    def get_body(self):
        return self.object.abbreviate()


@register(Message)
class MessageAdapter(BaseAdapter):
    mailer_class = MessageMailer
    webpusher_class = MessageWebpusher

    def get_object_url(self):
        return self.object.resolve_url(self.object.recipient)
