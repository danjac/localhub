# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model

from localhub.posts.models import Post
from localhub.posts.templatetags.posts_tags import is_post_oembed


class TestIsPostOembed:
    def test_not_oembed(self, rf):
        post = Post()
        req = rf.get("/")
        req.do_not_track = False
        assert not is_post_oembed({"request": req}, get_user_model()(), post)

    def test_if_allowed(self, rf):
        req = rf.get("/")
        req.do_not_track = False
        post = Post(url="https://www.youtube.com/watch?v=eLeIJtLebZk")
        assert is_post_oembed({"request": req}, get_user_model()(), post)

    def test_if_not_allowed(self, rf):
        req = rf.get("/")
        req.do_not_track = True
        post = Post(url="https://www.youtube.com/watch?v=eLeIJtLebZk")
        assert not is_post_oembed({"request": req}, get_user_model()(), post)
