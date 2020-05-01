# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.apps.activities.forms import ActivityForm
from localhub.forms.widgets import ClearableImageInput
from localhub.utils.exif import Exif

from .models import Photo

logger = logging.getLogger(__name__)


class PhotoForm(ActivityForm):
    class InvalidGPSLocation(ValueError):
        ...

    extract_gps_data = forms.BooleanField(
        label=_("Extract GPS data from image if available"), required=False,
    )

    clear_gps_data = forms.BooleanField(
        label=_("Clear GPS data from image"), required=False,
    )

    class Meta(ActivityForm.Meta):
        model = Photo
        fields = (
            "title",
            "hashtags",
            "mentions",
            "image",
            "extract_gps_data",
            "clear_gps_data",
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

        if self.instance.has_map():
            self.fields["extract_gps_data"].label = _(
                "Re-extract GPS data from image if available"
            )
        else:
            del self.fields["clear_gps_data"]

    def clean(self):
        cleaned_data = super(PhotoForm, self).clean()
        try:
            image = cleaned_data["image"]
        except KeyError:
            return cleaned_data

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if cleaned_data.get("clear_gps_data"):
            latitude, longitude = (None, None)

        elif cleaned_data["extract_gps_data"]:

            try:
                latitude, longitude = Exif.from_image(image).locate()
            except Exif.Invalid:
                latitude, longitude = (None, None)

        cleaned_data["latitude"] = latitude
        cleaned_data["longitude"] = longitude

        # try and get title from photo if missing
        if not cleaned_data["title"]:
            cleaned_data["title"] = image.name
        return cleaned_data
