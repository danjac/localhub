# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from icalendar import Calendar, Event as CalendarEvent

from django.http import HttpRequest, HttpResponse

from communikit.activities.views import SingleActivityView
from communikit.events.models import Event


class EventDownloadView(SingleActivityView):
    model = Event

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        event = CalendarEvent()

        event.add("dtstart", self.object.starts)
        event.add("dtstamp", self.object.starts)
        if self.object.ends:
            event.add("dtend", self.object.ends)
        event.add("summary", self.object.title)

        location = self.object.full_location
        if location:
            event.add("location", self.object.location)

        calendar = Calendar()
        calendar.add_component(event)

        response = HttpResponse(content_type="text/calendar")
        response.write(calendar.to_ical())
        return response


event_download_view = EventDownloadView.as_view()
