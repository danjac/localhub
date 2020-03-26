# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.forms.widgets import ClearableImageInput

from . import exif
from .models import Photo

logger = logging.getLogger(__name__)


class PhotoForm(ActivityForm):

    extract_geolocation_data = forms.BooleanField(
        label=_("Extract geolocation data from image if available"), required=False,
    )

    clear_geolocation_data = forms.BooleanField(
        label=_("Clear geolocation data from image"), required=False,
    )

    class Meta(ActivityForm.Meta):
        model = Photo
        fields = (
            "title",
            "additional_tags",
            "image",
            "extract_geolocation_data",
            "clear_geolocation_data",
            "description",
            "allow_comments",
            "artist",
            "original_url",
            "cc_license",
            "latitude",
            "longitude",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["image"].widget = ClearableImageInput()
        self.fields["latitude"].widget = forms.HiddenInput()
        self.fields["longitude"].widget = forms.HiddenInput()

        # we will try and use the photo filename if no title provided
        self.fields["title"].required = False

        if not self.instance.has_map():
            del self.fields["clear_geolocation_data"]

    def clean(self):
        cleaned_data = super(PhotoForm, self).clean()

        if self.cleaned_data.get("clear_geolocation_data"):
            cleaned_data["latitude"] = None
            cleaned_data["longitude"] = None
        elif self.cleaned_data["extract_geolocation_data"]:
            try:
                lat, lng = exif.get_geolocation_data_from_image(
                    self.cleaned_data["image"]
                )
                cleaned_data["latitude"] = lat
                cleaned_data["longitude"] = lng
            except exif.InvalidExifData as e:
                logger.error(e)

        # try and get title from photo if missing
        if not cleaned_data["title"]:
            cleaned_data["title"] = cleaned_data["image"].name
        return cleaned_data
