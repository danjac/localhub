# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.apps.users.factories import UserFactory

from ..factories import PostFactory
from ..templatetags.posts import render_opengraph_content

pytestmark = pytest.mark.django_db


class TestRenderOpengraphContent:
    def test_no_url(self, user, post):
        post = PostFactory(
            opengraph_description="test",
            opengraph_image="https://test.com/test.jpg",
            url="",
        )
        assert render_opengraph_content(user, post) == {"og_data": None, "post": post}

    def test_no_image(self, user):
        post = PostFactory(
            opengraph_description="test",
            opengraph_image="",
            url="http://imgur.com/test",
        )
        assert render_opengraph_content(user, post) == {
            "og_data": {"description": "test", "image": ""},
            "post": post,
        }

    def test_image_unsafe(self, user):
        post = PostFactory(
            url="http://imgur.com/test",
            opengraph_description="test",
            opengraph_image="http://imgur.com/cat.png",
        )
        assert render_opengraph_content(user, post) == {
            "og_data": {"description": "test", "image": ""},
            "post": post,
        }

    def test_image_safe(self, user):
        post = PostFactory(
            url="http://imgur.com/test",
            opengraph_description="test",
            opengraph_image="https://imgur.com/cat.png",
        )
        assert render_opengraph_content(user, post) == {
            "og_data": {"description": "test", "image": "https://imgur.com/cat.png"},
            "post": post,
        }

    def test_image_blocked_by_user(self):

        user = UserFactory(show_external_images=True)

        post = PostFactory(
            url="http://imgur.com/test",
            opengraph_description="test",
            opengraph_image="http://imgur.com/cat.png",
        )
        assert render_opengraph_content(user, post) == {
            "og_data": {"description": "test", "image": ""},
            "post": post,
        }
