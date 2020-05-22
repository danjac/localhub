# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import PhotoSerializer

pytestmark = pytest.mark.django_db


class TestPhotoSerializer:
    def test_serialize_photo(self, photo):
        data = PhotoSerializer(photo).data
        assert data["title"] == photo.title
        assert data["small_image_url"].endswith(".jpg")
        assert data["large_image_url"].endswith(".jpg")
        assert data["endpoints"]["detail"].endswith(f"/api/photos/{photo.id}/")
