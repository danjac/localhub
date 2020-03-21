# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import ClearableImageInput, TypeaheadInput

from . import exif
from .models import Photo

logger = logging.getLogger(__name__)


class PhotoForm(forms.ModelForm):

    extract_geolocation_data = forms.BooleanField(
        label=_("Extract geolocation data from image if available"), required=False,
    )

    class Meta:

        model = Photo
        fields = (
            "title",
            "additional_tags",
            "image",
            "extract_geolocation_data",
            "description",
            "allow_comments",
            "artist",
            "original_url",
            "cc_license",
            "latitude",
            "longitude",
        )
        widgets = {
            "title": TypeaheadInput,
            "additional_tags": TypeaheadInput(search_mentions=False),
            "image": ClearableImageInput,
            "latitude": forms.HiddenInput,
            "longitude": forms.HiddenInput,
        }
        help_texts = {
            "additional_tags": _(
                "Hashtags can also be added to title and description."
            ),
        }
        labels = {"additional_tags": _("Tags")}

    def clean(self):
        cleaned_data = super(PhotoForm, self).clean()
        if self.cleaned_data["extract_geolocation_data"]:
            try:
                lat, lng = exif.get_geolocation_data_from_image(
                    self.cleaned_data["image"]
                )
                cleaned_data["latitude"] = lat
                cleaned_data["longitude"] = lng
            except exif.InvalidExifData as e:
                logger.error(e)
        return cleaned_data
