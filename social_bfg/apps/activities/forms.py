# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from social_bfg.forms import TypeaheadInput

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "title",
            "hashtags",
            "mentions",
            "description",
            "allow_comments",
        )
        labels = {
            "title": _("Title"),
            "hashtags": _("#tags"),
            "mentions": _("@mentions"),
        }
        widgets = {
            "title": TypeaheadInput,
        }
        help_texts = {
            "hashtags": _("#tags can also be added to title and description."),
            "mentions": _("@mentions can also be added to title and description."),
        }


class ActivityTagsForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ("hashtags",)
        labels = {"hashtags": _("#tags")}
