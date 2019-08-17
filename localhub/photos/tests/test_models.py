# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.conf import settings

from localhub.photos.models import Photo

pytestmark = pytest.mark.django_db


class TestPhotoModel:

    def test_reshare(self, photo: Photo, user: settings.AUTH_USER_MODEL):

        reshared = photo.reshare(user)
        assert reshared.title == photo.title
        assert reshared.image == photo.image
        assert reshared.is_reshare
        assert reshared.parent == photo
        assert reshared.community == photo.community
        assert reshared.owner == user
