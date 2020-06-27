# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.activities.notifications import (
    ActivityAdapter,
    ActivityHeadersMixin,
    ActivityMailer,
    ActivityWebpusher,
)
from localhub.notifications.decorators import register

# Local
from .models import Poll


class PollHeadersMixin(ActivityHeadersMixin):
    HEADERS = ActivityHeadersMixin.HEADERS + [
        ("vote", _("%(actor)s has voted in your poll")),
    ]


class PollMailer(PollHeadersMixin, ActivityMailer):
    ...


class PollWebpusher(PollHeadersMixin, ActivityWebpusher):
    ...


@register(Poll)
class PollAdapter(ActivityAdapter):
    ALLOWED_VERBS = ActivityAdapter.ALLOWED_VERBS + ["vote"]

    mailer_class = PollMailer
    webpusher_class = PollWebpusher
