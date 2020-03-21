# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from .. import exif


class TestConvertToDegress:
    def test_valid(self):
        value = ((61, 1), (3, 1), (27, 1))
        assert exif.convert_to_degress(value) == pytest.approx(61, 0.5)

    def test_invalid(self):
        value = (
            (61, 1),
            (3, 1),
        )
        with pytest.raises(IndexError):
            exif.convert_to_degress(value)


class TestExtractGpsData:
    def test_ok(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "E",
        }
        mocker.patch("localhub.photos.exif.build_gps_data", return_value=data)
        lat, lng = exif.extract_gps_data(data)
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_latitude_ref_south(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "S",
            "GPSLongitudeRef": "E",
        }
        mocker.patch("localhub.photos.exif.build_gps_data", return_value=data)
        lat, lng = exif.extract_gps_data(data)
        assert lat == pytest.approx(-61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_longitude_ref_west(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLongitude": ((61, 1), (3, 1), (27, 1)),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "W",
        }
        mocker.patch("localhub.photos.exif.build_gps_data", return_value=data)
        lat, lng = exif.extract_gps_data(data)
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(-61, 0.5)

    def test_missing_data(self, mocker):
        mocker.patch("localhub.photos.exif.build_gps_data", return_value={})
        with pytest.raises(exif.InvalidExifData):
            exif.extract_gps_data({})

    def test_bad_degress(self, mocker):
        data = {
            "GPSLatitude": ((61, 1), (3, 1),),
            "GPSLongitude": ((61, 1), (3, 1),),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "E",
        }
        mocker.patch("localhub.photos.exif.build_gps_data", return_value=data)
        with pytest.raises(exif.InvalidExifData):
            exif.extract_gps_data(data)
