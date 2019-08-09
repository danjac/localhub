# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytz

from datetime import datetime
from typing import Any, Dict

from django import forms
from django.utils.timezone import localtime, make_aware
from django.utils.translation import gettext_lazy as _

from localhub.core.forms.fields import CalendarField
from localhub.events.models import Event


class EventForm(forms.ModelForm):

    starts = CalendarField(label=_("Event starts"))
    ends = CalendarField(label=_("Event ends"), required=False)

    class Meta:
        model = Event
        fields = (
            "title",
            "starts",
            "ends",
            "timezone",
            "url",
            "venue",
            "ticket_price",
            "ticket_vendor",
            "street_address",
            "locality",
            "postal_code",
            "region",
            "country",
            "description",
            "allow_comments",
        )
        localized_fields = ("starts", "ends")

        help_texts = {
            "timezone": _("Start and end times will be shown in this timezone")
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # convert the UTC stored value into the local time the user
        # originally entered according to their timezone. The final value
        # must be UTC, otherwise the field will just convert it again
        # to the database value.

        def _convert_to_local(value: datetime) -> datetime:
            return make_aware(
                localtime(value, self.instance.timezone).replace(tzinfo=None),
                pytz.UTC,
                is_dst=True,
            )

        if self.instance.starts:
            self.initial["starts"] = _convert_to_local(self.instance.starts)
        if self.instance.ends:
            self.initial["ends"] = _convert_to_local(self.instance.ends)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        timezone = cleaned_data["timezone"]

        # We don't want to do a timezone conversion, just preserve
        # the user entered value. Make a naive datetime stripping out UTC
        # and just set the timezone. Then do a timezone conversion
        # back to UTC to get the actual UTC value we want to store in the
        # database.

        # for example, if the user enters starts value 09:00 and timezone
        # Helsinki, we store the value in the database as 06:00 UTC.

        def _convert_to_utc(value: datetime) -> datetime:
            return localtime(
                make_aware(value.replace(tzinfo=None), timezone, is_dst=True),
                pytz.UTC,
            )

        cleaned_data["starts"] = _convert_to_utc(cleaned_data["starts"])

        # do the same with ends, if it's provided

        ends = cleaned_data.get("ends")
        if ends:
            cleaned_data["ends"] = _convert_to_utc(ends)
        return cleaned_data
