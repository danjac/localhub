# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms

from communikit.core.forms.fields import CalendarField
from communikit.events.models import Event


class EventForm(forms.ModelForm):

    starts = CalendarField()
    ends = CalendarField(required=False)

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
