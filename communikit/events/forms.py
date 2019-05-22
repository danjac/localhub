# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms

from communikit.events.models import Event
from communikit.events.widgets import CalendarWidget


class EventForm(forms.ModelForm):

    starts = forms.SplitDateTimeField(widget=CalendarWidget())
    ends = forms.SplitDateTimeField(widget=CalendarWidget())

    class Meta:
        model = Event
        fields = (
            "title",
            "starts",
            "ends",
            "url",
            "venue",
            "street_address",
            "locality",
            "postal_code",
            "region",
            "country",
            "description",
        )
        # widgets = {"starts": CalendarWidget(), "ends": CalendarWidget()}
