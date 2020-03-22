# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..factories import PhotoFactory
from ..forms import PhotoForm

pytestmark = pytest.mark.django_db


def get_form_data(image, **overrides):
    data = {
        "title": "test image",
        "additional_tags": "",
        "extract_geolocation_data": False,
        "description": "",
        "allow_comments": True,
        "artist": "",
        "original_url": "",
        "cc_license": "",
        "latitude": None,
        "longitude": None,
    }
    data.update(overrides)
    return data, {"image": image}


class TestPhotoForm:
    def test_remove_geolocation_data_if_not_latlng(self, photo, fake_image, mocker):

        form = PhotoForm(
            instance=photo,
            *get_form_data(
                image=fake_image,
                extract_geolocation_data=True,
                remove_geolocation_data=False,
            )
        )

        assert "remove_geolocation_data" not in form.fields
        assert form.is_valid()

        mocker.patch(
            "localhub.photos.exif.get_geolocation_data_from_image",
            return_value=(61, 24),
        )
        assert form.is_valid()

        cleaned_data = form.clean()
        assert cleaned_data["latitude"] == 61
        assert cleaned_data["longitude"] == 24

    def test_remove_geolocation_data_if_latlng(self, fake_image, mocker):

        photo = PhotoFactory(latitude=61, longitude=24)

        form = PhotoForm(
            instance=photo,
            *get_form_data(image=fake_image, remove_geolocation_data=True)
        )

        mocker.patch(
            "localhub.photos.exif.get_geolocation_data_from_image",
            return_value=(61, 24),
        )

        assert "remove_geolocation_data" in form.fields
        assert form.is_valid()

        cleaned_data = form.clean()
        assert cleaned_data["latitude"] is None
        assert cleaned_data["longitude"] is None

    def test_if_not_extract_geolocation_data(self, fake_image, mocker):

        form = PhotoForm(*get_form_data(image=fake_image))
        assert "remove_geolocation_data" not in form.fields

        mocker.patch(
            "localhub.photos.exif.get_geolocation_data_from_image",
            return_value=(61, 24),
        )
        assert form.is_valid()

        cleaned_data = form.clean()
        assert cleaned_data["latitude"] is None
        assert cleaned_data["longitude"] is None

    def test_if_extract_geolocation_data(self, fake_image, mocker):

        form = PhotoForm(
            *get_form_data(image=fake_image, extract_geolocation_data=True)
        )
        mocker.patch(
            "localhub.photos.exif.get_geolocation_data_from_image",
            return_value=(61, 24),
        )
        assert form.is_valid()

        cleaned_data = form.clean()
        assert cleaned_data["latitude"] == 61
        assert cleaned_data["longitude"] == 24

    def test_if_extract_geolocation_data_false(self, fake_image, mocker):

        form = PhotoForm(
            *get_form_data(image=fake_image, extract_geolocation_data=True)
        )
        mocker.patch(
            "localhub.photos.exif.get_geolocation_data_from_image",
            return_value=(None, None),
        )

        assert form.is_valid()

        cleaned_data = form.clean()
        assert cleaned_data["latitude"] is None
        assert cleaned_data["longitude"] is None
