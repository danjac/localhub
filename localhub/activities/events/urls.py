# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.urls import path

# Localhub
from localhub.activities.urls.generic import create_activity_urls

# Local
from . import views
from .forms import EventForm
from .models import Event

app_name = "events"


urlpatterns = create_activity_urls(
    Event,
    EventForm,
    create_view_class=views.EventCreateView,
    update_view_class=views.EventUpdateView,
    detail_view_class=views.EventDetailView,
    list_view_class=views.EventListView,
)

urlpatterns += [
    path("calendar/", views.event_calendar_view, name="calendar"),
    path("<int:pk>~attend/", views.event_attend_view, name="attend"),
    path("<int:pk>~unattend/", views.event_unattend_view, name="unattend"),
    path("<int:pk>~cancel/", views.event_cancel_view, name="cancel"),
    path("<int:pk>~download/", views.event_download_view, name="download"),
]
