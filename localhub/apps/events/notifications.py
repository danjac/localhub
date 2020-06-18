# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.translation import gettext_lazy as _

# Localhub
# Social-BFG
from localhub.apps.activities.notifications import (
    ActivityAdapter,
    ActivityHeadersMixin,
    ActivityMailer,
    ActivityWebpusher,
)
from localhub.apps.notifications.decorators import register

# Local
from .models import Event


class EventHeadersMixin(ActivityHeadersMixin):
    HEADERS = ActivityHeadersMixin.HEADERS + [
        ("attend", _("%(actor)s is attending your event")),
        ("cancel", _("%(actor)s has canceled an event")),
    ]


class EventMailer(EventHeadersMixin, ActivityMailer):
    ...


class EventWebpusher(EventHeadersMixin, ActivityWebpusher):
    ...


@register(Event)
class EventAdapter(ActivityAdapter):
    ALLOWED_VERBS = ActivityAdapter.ALLOWED_VERBS + ["attend", "cancel"]

    mailer_class = EventMailer
    webpusher_class = EventWebpusher
