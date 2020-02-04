# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model

from ..models import Post
from ..templatetags.posts_tags import is_post_oembed


class TestIsPostOembed:
    def test_not_oembed(self, rf):
        post = Post()
        user = get_user_model()
        user.show_embedded_content = True
        req = rf.get("/")
        assert not is_post_oembed({"request": req}, user, post)

    def test_if_allowed(self, rf):
        req = rf.get("/")
        user = get_user_model()
        user.show_embedded_content = True
        post = Post(url="https://www.youtube.com/watch?v=eLeIJtLebZk")
        assert is_post_oembed({"request": req}, user, post)

    def test_if_not_allowed(self, rf):
        req = rf.get("/")
        user = get_user_model()
        user.show_embedded_content = False
        post = Post(url="https://www.youtube.com/watch?v=eLeIJtLebZk")
        assert not is_post_oembed({"request": req}, user, post)
