# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms import TypeaheadInput

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "title",
            "additional_tags",
            "mentions",
            "description",
            "allow_comments",
        )
        labels = {
            "title": _("Title"),
            "additional_tags": _("#tags"),
            "mentions": _("@mentions"),
        }
        widgets = {
            "title": TypeaheadInput,
        }
        help_texts = {
            "additional_tags": _("#tags can also be added to title and description."),
            "mentions": _("@mentions can also be added to title and description."),
        }


class ActivityTagsForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ("additional_tags",)
        labels = {"additional_tags": _("Tags")}
