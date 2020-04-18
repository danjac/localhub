# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class ClearableImageInput(forms.ClearableFileInput):
    template_name = "includes/forms/widgets/clearable_image.html"


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
            data["tag_search_url"] = reverse("hashtags:autocomplete_list")
        return data

    def format_value(self, value):
        """Replace any commas with space, remove any extra spaces"""
        if not value:
            return value
        return " ".join(value.replace(",", " ").strip().split())


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
            {
                "data-action": "click->calendar#toggle",
                "data-target": "calendar.dateInput",
                "autocomplete": "off",
                "placeholder": _("DD/MM/YYYY"),
            }
        )
        time_attrs = kwargs.pop("time_attrs", {})
        time_attrs.update(
            {"autocomplete": "off", "placeholder": _("HH:MM"), "type": "time",}
        )
        super().__init__(
            date_attrs=date_attrs,
            date_format="%d/%m/%Y",
            time_attrs=time_attrs,
            time_format="%H:%M",
            *args,
            **kwargs
        )
