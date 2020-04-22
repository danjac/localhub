# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.forms.widgets import ClearableImageInput
from localhub.utils.exif import Exif

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

        if self.cleaned_data.get("clear_gps_data"):
            cleaned_data["latitude"] = None
            cleaned_data["longitude"] = None
        elif self.cleaned_data["extract_gps_data"]:
            try:
                lat, lng = Exif.from_image(self.cleaned_data["image"]).locate()
                cleaned_data["latitude"] = lat
                cleaned_data["longitude"] = lng
            except Exif.Invalid as e:
                logger.error(e)
                cleaned_data["latitude"] = None
                cleaned_data["longitude"] = None

        # try and get title from photo if missing
        if not cleaned_data["title"]:
            cleaned_data["title"] = cleaned_data["image"].name
        return cleaned_data
