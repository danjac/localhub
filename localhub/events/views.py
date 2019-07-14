# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from icalendar import Calendar, Event as CalendarEvent

from django.http import HttpRequest, HttpResponse

from localhub.activities.views import SingleActivityView
from localhub.events.models import Event


class EventDownloadView(SingleActivityView):
    """
    Generates a calendar .ics file.
    """
    model = Event

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        event = CalendarEvent()

        starts = self.object.get_starts_with_tz()
        ends = self.object.get_ends_with_tz()

        event.add("dtstart", starts)
        event.add("dtstamp", starts)
        if ends:
            event.add("dtend", ends)
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
