# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytz
from django.utils.timezone import localtime, make_aware
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.forms.fields import CalendarField

from .models import Event

DATE_FORMATS = ["%d/%m/%Y"]


class EventForm(ActivityForm):

    starts = CalendarField(label=_("Event starts"), input_date_formats=DATE_FORMATS)

    ends = CalendarField(
        label=_("Event ends"), required=False, input_date_formats=DATE_FORMATS
    )

    class Meta(ActivityForm.Meta):
        model = Event
        fields = (
            "title",
            "additional_tags",
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

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["timezone"].help_text = _(
            "Start and end times will be shown in this timezone"
        )

        # convert the UTC stored value into the local time the user
        # originally entered according to their timezone. The final value
        # must be UTC, otherwise the field will just convert it again
        # to the database value.

        for field in ("starts", "ends"):
            value = getattr(self.instance, field)
            if value:
                self.initial[field] = make_aware(
                    localtime(value, self.instance.timezone).replace(tzinfo=None),
                    pytz.UTC,
                    is_dst=True,
                )

    def clean(self):
        cleaned_data = super().clean()
        timezone = cleaned_data["timezone"]

        # We don't want to do a timezone conversion, just preserve
        # the user entered value. Make a naive datetime stripping out UTC
        # and just set the timezone. Then do a timezone conversion
        # back to UTC to get the actual UTC value we want to store in the
        # database.

        # for example, if the user enters starts value 09:00 and timezone
        # Helsinki, we store the value in the database as 06:00 UTC.

        for field in ("starts", "ends"):
            value = cleaned_data.get(field)
            if value:
                cleaned_data[field] = localtime(
                    make_aware(value.replace(tzinfo=None), timezone, is_dst=True),
                    pytz.UTC,
                )
        return cleaned_data
