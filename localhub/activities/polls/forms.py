# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.activities.forms import ActivityForm

# Local
from .models import Poll


class PollForm(ActivityForm):
    class Meta(ActivityForm.Meta):
        model = Poll

        fields = ActivityForm.Meta.fields + ("allow_voting",)