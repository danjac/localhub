# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from django.utils.translation import gettext_lazy as _


class CalendarWidget(forms.SplitDateTimeWidget):
    template_name = "includes/forms/widgets/calendar.html"
    input_type = "calendar"

    def __init__(self, *args, **kwargs):
        date_attrs = kwargs.pop("date_attrs", {})
        date_attrs.update(
            {"data-target": "calendar.dateInput", "placeholder": _("Date")}
        )
        time_attrs = kwargs.pop("time_attrs", {})
        time_attrs.update(
            {"data-target": "calendar.timeInput", "placeholder": _("Time")}
        )
        super().__init__(
            date_attrs=date_attrs,
            time_attrs=time_attrs,
            time_format="%H:%M",
            *args,
            **kwargs
        )
