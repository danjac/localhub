# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

pytestmark = pytest.mark.django_db


class TestPhotoModel:
    def test_reshare(self, photo, user):

        reshared = photo.reshare(user)
        assert reshared.title == photo.title
        assert reshared.image == photo.image
        assert reshared.is_reshare
        assert reshared.parent == photo
        assert reshared.community == photo.community
        assert reshared.owner == user
