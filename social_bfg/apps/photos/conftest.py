# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.utils.exif import Exif

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
        "social_bfg.utils.exif.Exif.from_image", return_value=MockExif(),
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
        "social_bfg.utils.exif.Exif.from_image", return_value=MockExif(),
    )

    yield


@pytest.fixture
def photo_for_member(member):
    return PhotoFactory(owner=member.member, community=member.community)
