# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Localhub
from localhub.common.utils.exif import Exif

# Local
from .factories import PhotoFactory


@pytest.fixture()
def mock_invalid_exif(mocker):
    class MockExif:
        def locate(self):
            raise Exif.Invalid()

        def rotate(self):
            raise Exif.Invalid()

    mocker.patch(
        "localhub.common.utils.exif.Exif.from_image",
        return_value=MockExif(),
    )

    yield


@pytest.fixture()
def mock_exif(mocker):
    class MockExif:
        def locate(self):
            return (61, 24)

        def rotate(self):
            pass

    mocker.patch(
        "localhub.common.utils.exif.Exif.from_image",
        return_value=MockExif(),
    )

    yield


@pytest.fixture
def photo_for_member(member):
    return PhotoFactory(owner=member.member, community=member.community)
