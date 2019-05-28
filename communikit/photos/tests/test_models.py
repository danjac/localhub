# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.utils.encoding import force_str

from communikit.photos.models import Photo

pytestmark = pytest.mark.django_db


class TestPhotoModel:
    def test_breadcrumbs(self, photo: Photo):
        assert photo.get_breadcrumbs() == [
            ("/", "Home"),
            ("/photos/", "Photos"),
            (f"/photos/{photo.id}/", force_str(photo.title)),
        ]
