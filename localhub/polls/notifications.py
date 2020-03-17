# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.activities.notifications import (
    ActivityMailer,
    ActivityAdapter,
    ActivityWebpusher,
)
from localhub.notifications.decorators import register

from .models import Poll

POLL_HEADERS = [
    ("vote", _("%(actor)s has voted in your poll")),
]


class PollMailer(ActivityMailer):
    HEADERS = ActivityMailer.HEADERS + POLL_HEADERS


class PollWebpusher(ActivityWebpusher):
    HEADERS = ActivityWebpusher.HEADERS + POLL_HEADERS


@register(Poll)
class PollAdapter(ActivityAdapter):
    mailer_class = PollMailer
    webpusher_class = PollWebpusher
