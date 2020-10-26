# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.activities.forms import ActivityForm

# Local
from .models import Poll


class PollForm(ActivityForm):
    class Meta(ActivityForm.Meta):
        model = Poll

        fields = ActivityForm.Meta.fields + ("allow_voting",)
        help_texts = {
            **ActivityForm.Meta.help_texts,
            "allow_voting": _("Voting is only allowed on public polls."),
        }
