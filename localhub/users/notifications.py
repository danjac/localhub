# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from localhub.notifications.adapter import Adapter, Mailer, Webpusher
from localhub.notifications.decorators import register

HEADERS = [
    ("new_follower", _("%(actor)s has started following you")),
    ("new_member", _("%(actor)s has just joined this community")),
    ("update", _("%(actor)s has updated their profile")),
]


class UserMailer(Mailer):
    def get_subject(self):
        return dict(HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name()
        }


class UserWebpusher(Webpusher):
    def get_header(self):
        return dict(HEADERS)[self.adapter.verb] % {
            "actor": self.adapter.actor.get_display_name()
        }

    def get_body(self):
        return (
            f"@{self.adapter.actor.username} ({self.adapter.actor.get_display_name()})"
        )


@register(get_user_model())
class UserAdapter(Adapter):
    ALLOWED_VERBS = ["new_follower", "new_member", "update"]

    mailer_class = UserMailer
    webpusher_class = UserWebpusher
