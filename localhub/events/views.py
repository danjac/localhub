# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpRequest, HttpResponse

from localhub.activities.views.generic import SingleActivityView
from localhub.events.models import Event


class EventDownloadView(SingleActivityView):
    """
    Generates a calendar .ics file.
    """

    model = Event

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: Event = self.get_object()

        response = HttpResponse(content_type="text/calendar")
        response.write(self.object.to_ical())
        return response


event_download_view = EventDownloadView.as_view()
