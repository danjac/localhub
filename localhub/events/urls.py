# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.urls import path

from localhub.activities.urls.generic import create_activity_urls

from .forms import EventForm
from .models import Event
from .views import (
    EventCreateView,
    event_attend_view,
    event_cancel_view,
    event_download_view,
    event_unattend_view,
)

app_name = "events"


urlpatterns = create_activity_urls(Event, EventForm, create_view_class=EventCreateView)

urlpatterns += [
    path("<int:pk>~attend/", event_attend_view, name="attend"),
    path("<int:pk>~unattend/", event_unattend_view, name="unattend"),
    path("<int:pk>~cancel/", event_cancel_view, name="cancel"),
    path("<int:pk>~download/", event_download_view, name="download"),
]
