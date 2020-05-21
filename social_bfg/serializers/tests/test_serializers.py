# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from .. import GenericObjectSerializer

pytestmark = pytest.mark.django_db


class TestGenericObjectSerializer:
    def test_serialize_post(self, post):
        data = GenericObjectSerializer(post).data
        assert data["id"] == post.id
        assert data["title"] == post.title
        assert data["object_type"] == "post"
