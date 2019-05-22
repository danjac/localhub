# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms


class CalendarWidget(forms.DateTimeInput):
    template_name = "includes/forms/widgets/calendar.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({"data-target": "calendar.input"})
