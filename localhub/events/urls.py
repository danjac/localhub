# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.urls import path

from localhub.activities.views import create_activity_urls
from localhub.events.forms import EventForm
from localhub.events.models import Event
from localhub.events.views import event_download_view


app_name = "events"


urlpatterns = create_activity_urls(Event, EventForm)

urlpatterns += [
    path("<int:pk>~download/", event_download_view, name="download")
]
