# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import TypeaheadInput

from .models import Poll


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ("title", "additional_tags", "description", "allow_comments")

        widgets = {
            "title": TypeaheadInput,
            "additional_tags": TypeaheadInput(search_mentions=False),
        }
        help_texts = {
            "additional_tags": _(
                "Hashtags can also be added to title and description."
            ),
        }
        labels = {"additional_tags": _("Tags")}

