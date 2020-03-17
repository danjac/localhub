# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapters import DefaultAdapter, Mailer, Webpusher
from localhub.notifications.decorators import register

from .utils import user_display

HEADERS = [
    ("new_follower", _("Someone has started following you")),
    ("new_member", _("Someone has just joined this community")),
]


class UserMailer(Mailer):
    HEADERS = HEADERS

    def get_subject(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }


class UserWebpusher(Webpusher):
    HEADERS = HEADERS

    def get_header(self):
        return dict(self.HEADERS)[self.adapter.verb] % {
            "actor": user_display(self.adapter.actor)
        }

    def get_body(self):
        return user_display(self.adapter.actor)


@register(get_user_model())
class UserAdapter(DefaultAdapter):
    mailer_class = UserMailer
    webpusher_class = UserWebpusher
