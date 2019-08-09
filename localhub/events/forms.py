# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from localhub.core.forms.fields import CalendarField
from localhub.events.models import Event

calendar_help_text = _(
    "Time will be stored in UTC timezone. It will be shown in the timezone you select below."  # noqa
)


class EventForm(forms.ModelForm):

    starts = CalendarField(
        label=_("Event starts"), help_text=calendar_help_text
    )
    ends = CalendarField(
        label=_("Event ends"), help_text=calendar_help_text, required=False
    )

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

    def save(self, *args, **kwargs):
        with timezone.override(self.cleaned_data["timezone"]):
            instance = super().save(*args, **kwargs)
        return instance
