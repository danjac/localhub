# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.urls import path

from communikit.activities.views import create_activity_urls
from communikit.events.forms import EventForm
from communikit.events.models import Event
from communikit.events.views import event_download_view


app_name = "events"


urlpatterns = create_activity_urls(model=Event, form_class=EventForm)

urlpatterns += [
    path("<int:pk>~download/", event_download_view, name="download")
]
