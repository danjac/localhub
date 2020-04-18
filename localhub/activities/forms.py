# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import TypeaheadInput
from localhub.hashtags.constants import HASHTAGS_TYPEAHEAD_URL
from localhub.users.constants import MENTIONS_TYPEAHEAD_URL

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "title",
            "additional_tags",
            "description",
            "allow_comments",
        )
        labels = {"title": _("Title"), "additional_tags": _("Tags")}
        widgets = {
            "title": TypeaheadInput(
                typeahead_urls=(HASHTAGS_TYPEAHEAD_URL, MENTIONS_TYPEAHEAD_URL)
            ),
            "additional_tags": TypeaheadInput(typeahead_urls=(HASHTAGS_TYPEAHEAD_URL,)),
        }
        help_texts = {
            "additional_tags": _(
                "Hashtags can also be added to title and description."
            ),
        }


class ActivityTagsForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ("additional_tags",)
        labels = {"additional_tags": _("Tags")}
        widgets = {
            "additional_tags": TypeaheadInput(typeahead_urls=(HASHTAGS_TYPEAHEAD_URL,)),
        }
