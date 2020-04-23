# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from localhub.activities.views.actions import BaseActivityActionView
from localhub.activities.views.mixins import ActivityQuerySetMixin

from ..models import Event


class EventCancelView(BaseActivityActionView):
    success_message = _("This event has been canceled")

    permission_required = "events.cancel"
    model = Event

    def post(self, request, *args, **kwargs):
        self.object.canceled = timezone.now()
        self.object.save()
        self.object.notify_on_cancel(self.request.user)
        return self.success_response()


event_cancel_view = EventCancelView.as_view()


class BaseEventAttendView(BaseActivityActionView):
    permission_required = "events.attend"
    is_success_ajax_response = True
    model = Event


class EventAttendView(BaseEventAttendView):
    success_message = _("You are now attending this event")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.add(self.request.user)
        self.object.notify_on_attend(self.request.user)
        return self.success_response()


event_attend_view = EventAttendView.as_view()


class EventUnattendView(BaseEventAttendView):
    success_message = _("You are no longer attending this event")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.attendees.remove(self.request.user)
        return self.success_response()


event_unattend_view = EventUnattendView.as_view()


class EventDownloadView(ActivityQuerySetMixin, SingleObjectMixin, View):
    """
    Generates a calendar .ics file.
    """

    model = Event

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        response = HttpResponse(content_type="text/calendar")
        response.write(self.object.to_ical())
        return response


event_download_view = EventDownloadView.as_view()
