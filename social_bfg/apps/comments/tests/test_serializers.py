# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
import pytest

# Local
from ..serializers import CommentSerializer

pytestmark = pytest.mark.django_db


class TestCommentSerializer:
    def test_serialize_comment(self, comment):
        data = CommentSerializer(comment).data
        assert data["markdown"] == comment.content.markdown()
        assert data["content_object"]["object_type"] == "post"
        assert data["content_object"]["title"] == comment.content_object.title
        assert data["owner"]["username"] == comment.owner.username
