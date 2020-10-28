# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..exif import Exif


class TestLocate:
    def mock_build_gps_dict(self, mocker, mock_data):
        mocker.patch(
            "localhub.common.utils.exif.Exif.build_gps_dict", return_value=mock_data
        )

    def test_ok(self, mocker):
        data = {
            "GPSLatitude": (61, 3, 1),
            "GPSLongitude": (61, 1, 3),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "E",
        }
        self.mock_build_gps_dict(mocker, data)
        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_latitude_ref_south(self, mocker):
        data = {
            "GPSLatitude": (61, 3, 1),
            "GPSLongitude": (61, 1, 3),
            "GPSLatitudeRef": "S",
            "GPSLongitudeRef": "E",
        }
        self.mock_build_gps_dict(mocker, data)

        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(-61, 0.5)
        assert lng == pytest.approx(61, 0.5)

    def test_ok_longitude_ref_west(self, mocker):
        data = {
            "GPSLatitude": (61, 3, 1),
            "GPSLongitude": (61, 1, 3),
            "GPSLatitudeRef": "N",
            "GPSLongitudeRef": "W",
        }
        self.mock_build_gps_dict(mocker, data)
        lat, lng = Exif(None, None).locate()
        assert lat == pytest.approx(61, 0.5)
        assert lng == pytest.approx(-61, 0.5)
