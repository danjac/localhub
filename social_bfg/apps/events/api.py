# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Social-BFG
from social_bfg.apps.activities.api.generic import ActivityViewSet

# Local
from .models import Event
from .serializers import EventSerializer


class EventViewSet(ActivityViewSet):
    model = Event
    serializer_class = EventSerializer
