# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import ClearableImageInput, TypeaheadInput

from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:

        model = Photo
        fields = (
            "title",
            "additional_tags",
            "image",
            "description",
            "allow_comments",
            "artist",
            "original_url",
            "cc_license",
        )
        widgets = {
            "title": TypeaheadInput,
            "additional_tags": TypeaheadInput(search_mentions=False),
            "image": ClearableImageInput,
        }
        help_texts = {
            "additional_tags": _(
                "Hashtags can also be added to title and description."
            ),
        }
        labels = {"additional_tags": _("Tags")}

