# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class TypeaheadInput(forms.TextInput):
    template_name = "includes/forms/widgets/typeahead.html"

    def __init__(self, attrs=None, search_mentions=True, search_hashtags=True):
        super().__init__(attrs)
        self.search_mentions = search_mentions
        self.search_hashtags = search_hashtags

    def get_context(self, name, value, attrs):
        data = super().get_context(name, value, attrs)
        if self.search_mentions:
            data["mention_search_url"] = reverse("users:autocomplete_list")
        if self.search_hashtags:
            data["tag_search_url"] = reverse("activities:tag_autocomplete_list")
        return data


class CalendarWidget(forms.SplitDateTimeWidget):
    """
    Custom SplitDateTimeWidget using a Javascript-generated
    calendar. Note that the CSS/JS code is bundled as part of the
    project assets and frontend framework and so is not
    included as separate Media assets with this widget.
    """

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
