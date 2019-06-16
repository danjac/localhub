# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Tuple

from django.urls import reverse
from django.utils.translation import gettext as _

from communikit.activities.views import (
    ActivityCreateView,
    ActivityDeleteView,
    ActivityDetailView,
    ActivityDislikeView,
    ActivityLikeView,
    ActivityListView,
    ActivityUpdateView,
)
from communikit.events.forms import EventForm
from communikit.events.models import Event


class EventCreateView(ActivityCreateView):
    model = Event
    form_class = EventForm

    def get_breadcrumbs(self) -> List[Tuple[str, str]]:
        return [
            (reverse("activities:stream"), _("Home")),
            (reverse("events:list"), _("Events")),
            (self.request.path, _("Submit Event")),
        ]


event_create_view = EventCreateView.as_view()


event_list_view = ActivityListView.as_view(model=Event, order_by="starts")

event_detail_view = ActivityDetailView.as_view(model=Event)

event_update_view = ActivityUpdateView.as_view(
    model=Event, form_class=EventForm
)

event_delete_view = ActivityDeleteView.as_view(model=Event)

event_like_view = ActivityLikeView.as_view(model=Event)

event_dislike_view = ActivityDislikeView.as_view(model=Event)
