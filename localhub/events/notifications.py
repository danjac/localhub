# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from localhub.apps.activities.notifications import (
    ActivityAdapter,
    ActivityMailer,
    ActivityWebpusher,
)
from localhub.apps.notifications.decorators import register

from .models import Event

EVENT_HEADERS = [
    ("attend", _("%(actor)s is attending your event")),
    ("cancel", _("%(actor)s has canceled an event")),
]


class EventMailer(ActivityMailer):
    HEADERS = ActivityMailer.HEADERS + EVENT_HEADERS


class EventWebpusher(ActivityWebpusher):
    HEADERS = ActivityWebpusher.HEADERS + EVENT_HEADERS


@register(Event)
class EventAdapter(ActivityAdapter):
    ALLOWED_VERBS = ActivityAdapter.ALLOWED_VERBS + ["attend", "cancel"]

    mailer_class = EventMailer
    webpusher_class = EventWebpusher
