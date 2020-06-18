# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import logging

# Django
from django import forms
from django.utils.translation import gettext_lazy as _

# Localhub
from localhub.apps.activities.forms import ActivityForm
from localhub.forms import ClearableImageInput, FormHelper
from localhub.utils.exif import Exif

# Local
from .models import Photo

logger = logging.getLogger(__name__)


class PhotoForm(ActivityForm):

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
            "description",
            "allow_comments",
            "extract_gps_data",
            "clear_gps_data",
            "artist",
            "original_url",
            "cc_license",
            "latitude",
            "longitude",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fieldsets = FormHelper(
            self,
            (
                None,
                (
                    "title",
                    "hashtags",
                    "mentions",
                    "image",
                    "extract_gps_data",
                    "clear_gps_data",
                    "description",
                    "allow_comments",
                ),
            ),
            (_("Additional Information"), ("artist", "original_url", "cc_license",)),
        )

        self.fields["image"].widget = ClearableImageInput()
        self.fields["latitude"].widget = forms.HiddenInput()
        self.fields["longitude"].widget = forms.HiddenInput()

        self.fields["original_url"].label = _("Original URL")

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

        try:
            exif = Exif.from_image(image)
        except Exif.Invalid:
            exif = None

        # try and rotate image if orientation provided

        if exif:
            try:
                exif.rotate()
            except Exif.Invalid:
                pass

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if cleaned_data.get("clear_gps_data"):
            latitude, longitude = (None, None)

        elif cleaned_data["extract_gps_data"]:

            try:
                latitude, longitude = exif.locate()
            except Exif.Invalid:
                latitude, longitude = (None, None)

        cleaned_data["latitude"] = latitude
        cleaned_data["longitude"] = longitude

        # try and get title from photo if missing
        if not cleaned_data["title"]:
            cleaned_data["title"] = image.name
        return cleaned_data
