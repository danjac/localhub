# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.photos.models import Photo

pytestmark = pytest.mark.django_db


class TestPhotoModel:
    def test_breadcrumbs(self, photo: Photo):
        breadcrumbs = photo.get_breadcrumbs()
        assert len(breadcrumbs) == 3
        assert breadcrumbs[2][0] == photo.get_absolute_url()
