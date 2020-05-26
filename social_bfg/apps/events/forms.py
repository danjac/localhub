# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import forms
from django.utils.timezone import localtime, make_aware
from django.utils.translation import gettext_lazy as _

# Third Party Libraries
import pytz

# Social-BFG
from social_bfg.apps.activities.forms import ActivityForm
from social_bfg.forms import CalendarField, CalendarWidget, FormHelper
from social_bfg.utils.geocode import geocode

# Local
from .models import Event

DATE_FORMATS = ["%d/%m/%Y"]


class EventForm(ActivityForm):

    starts = CalendarField(
        label=_("Event starts"),
        input_date_formats=DATE_FORMATS,
        widget=CalendarWidget(notify="event:starts", default_time="09:00"),
    )

    ends = CalendarField(
        label=_("Event ends"),
        required=False,
        input_date_formats=DATE_FORMATS,
        widget=CalendarWidget(listen="event:starts", default_time="09:00"),
        help_text=_("Leave empty if it's an all-day event"),
    )

    repeats_until = CalendarField(
        label=_("Repeat until"),
        input_date_formats=DATE_FORMATS,
        required=False,
        widget=CalendarWidget(listen="event:starts", default_time="09:00"),
    )

    clear_geolocation = forms.BooleanField(
        label=_("Remove event from map"), required=False
    )

    fetch_geolocation = forms.BooleanField(
        label=_("Add event to map if address provided"), required=False
    )

    class Meta(ActivityForm.Meta):
        model = Event
        fields = (
            "title",
            "hashtags",
            "mentions",
            "starts",
            "ends",
            "repeats",
            "repeats_until",
            "timezone",
            "url",
            "description",
            "allow_comments",
            "venue",
            "street_address",
            "locality",
            "postal_code",
            "region",
            "country",
            "clear_geolocation",
            "fetch_geolocation",
            "latitude",
            "longitude",
        )
        localized_fields = ("starts", "ends")

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fieldsets = FormHelper(
            self,
            (
                None,
                (
                    "title",
                    "hashtags",
                    "mentions",
                    "starts",
                    "ends",
                    "repeats",
                    "repeats_until",
                    "timezone",
                    "url",
                    "description",
                    "allow_comments",
                ),
            ),
            (
                _("Location"),
                (
                    "venue",
                    "street_address",
                    "locality",
                    "postal_code",
                    "region",
                    "country",
                    "clear_geolocation",
                    "fetch_geolocation",
                ),
            ),
        )
        self.fields["latitude"].widget = forms.HiddenInput()
        self.fields["longitude"].widget = forms.HiddenInput()

        self.fields["repeats"].help_text = _("Will repeat from the start date onwards")

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

        if self.instance.has_map():
            self.fields["fetch_geolocation"].label = _("Recalculate position on map")
        else:
            del self.fields["clear_geolocation"]

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

        if cleaned_data.get("clear_geolocation"):
            cleaned_data["latitude"], cleaned_data["longitude"] = None, None

        elif cleaned_data["fetch_geolocation"]:
            latitude, longitude = geocode(
                cleaned_data["street_address"],
                cleaned_data["locality"],
                cleaned_data["postal_code"],
                cleaned_data["country"],
            )
            if None in (latitude, longitude):
                raise forms.ValidationError(_("Unable to locate address on map"))
            cleaned_data["latitude"] = latitude
            cleaned_data["longitude"] = longitude

        return cleaned_data
