# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import PostSerializer

pytestmark = pytest.mark.django_db


class TestPostSerializer:
    def test_serialize_post(self, post):
        data = PostSerializer(post).data
        assert data["title"] == post.title
        assert data["owner"]["username"] == post.owner.username
