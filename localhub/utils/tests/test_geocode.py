# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from ..geocode import geocode


class TestGeocoder:
    def test_geocode_ok(self, mocker):
        class MockGoodOSMResult:
            latitude = 60
            longitude = 50

        mocker.patch(
            "localhub.utils.geocode.geolocator.geocode", return_value=MockGoodOSMResult,
        )

        assert geocode(
            street_address="Areenankuja 1",
            postal_code="20040",
            locality="Helsinki",
            country="FI",
        ) == (60, 50)

    def test_geocode_not_ok(self, mocker):

        mock_geocode = mocker.patch(
            "localhub.utils.geocode.geolocator.geocode", return_value=None
        )

        assert geocode(
            street_address="Areenankuja 1",
            postal_code="20040",
            locality="Helsinki",
            country="FI",
        ) == (None, None)

        assert mock_geocode.call_count == 1

    def test_geocode_location_missing_data(self, mocker):
        class MockGoodOSMResult:
            latitude = 60
            longitude = 50

        mock_geocode = mocker.patch(
            "localhub.utils.geocode.geolocator.geocode", return_value=MockGoodOSMResult,
        )

        assert geocode(
            street_address="Areenankuja 1", postal_code="20040", country="FI",
        ) == (None, None)

        assert mock_geocode.call_count == 0
