# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponse

from localhub.activities.views.generic import ActivityCreateView, BaseSingleActivityView

from .models import Event


class EventCreateView(ActivityCreateView):
    def get_form(self, data=None, files=None):
        form = super().get_form(data, files)
        form.initial["timezone"] = self.request.user.default_timezone
        return form


class EventDownloadView(BaseSingleActivityView):
    """
    Generates a calendar .ics file.
    """

    model = Event

    def get(self, request, *args, **kwargs):
        self.object: Event = self.get_object()

        response = HttpResponse(content_type="text/calendar")
        response.write(self.object.to_ical())
        return response


event_download_view = EventDownloadView.as_view()
