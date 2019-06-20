# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from communikit.activities.views import ActivityViewSet
from communikit.events.forms import EventForm
from communikit.events.models import Event

app_name = "events"


urlpatterns = ActivityViewSet(model=Event, form_class=EventForm).urls
