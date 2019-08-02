# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.posts.models import Post

pytestmark = pytest.mark.django_db


class TestTracker:
    def test_changed(self, post: Post):
        assert not post.description_tracker.changed()
        post.description = "testing changed"
        post.save()
        assert post.description_tracker.changed()
