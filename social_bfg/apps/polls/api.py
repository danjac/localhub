# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Social-BFG
from social_bfg.apps.activities.api.generic import ActivityViewSet

# Local
from .models import Poll
from .serializers import PollSerializer


class PollViewSet(ActivityViewSet):
    model = Poll
    serializer_class = PollSerializer
