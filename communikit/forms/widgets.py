# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms


class CalendarWidget(forms.SplitDateTimeWidget):
    template_name = "includes/forms/widgets/calendar.html"

    def __init__(self, *args, **kwargs):
        date_attrs = kwargs.pop("date_attrs", {})
        date_attrs.update({"data-target": "calendar.dateInput"})
        super().__init__(date_attrs=date_attrs, *args, **kwargs)
