# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.activities.notifications import (
    ActivityAdapter,
    ActivityMailer,
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
    ALLOWED_VERBS = ActivityAdapter.ALLOWED_VERBS + ["vote"]

    mailer_class = PollMailer
    webpusher_class = PollWebpusher
