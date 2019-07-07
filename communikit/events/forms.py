# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from communikit.core.forms.fields import CalendarField
from communikit.events.models import Event


class EventForm(forms.ModelForm):

    starts = CalendarField(
        label=_("Event starts"), help_text=_("Timezone UTC")
    )
    ends = CalendarField(
        label=_("Event ends"), help_text=_("Timezone UTC"), required=False
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
        )

        help_texts = {
            "timezone": _("All times will be shown in this timezone")
        }
