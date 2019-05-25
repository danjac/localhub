# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy

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


event_create_view = ActivityCreateView.as_view(
    model=Event, form_class=EventForm, success_url=reverse_lazy("events:list")
)

event_list_view = ActivityListView.as_view(model=Event, order_by="starts")

event_detail_view = ActivityDetailView.as_view(model=Event)

event_update_view = ActivityUpdateView.as_view(
    model=Event, form_class=EventForm
)

event_delete_view = ActivityDeleteView.as_view(
    model=Event, success_url=reverse_lazy("events:list")
)

event_like_view = ActivityLikeView.as_view(model=Event)

event_dislike_view = ActivityDislikeView.as_view(model=Event)
