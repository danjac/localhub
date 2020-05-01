# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone

import pytest

from bfg.apps.posts.factories import PostFactory

from ..templatetags.activities import (
    get_pinned_activity,
    is_oembed_url,
    render_activity,
)

pytestmark = pytest.mark.django_db


class TestRenderActivity:
    def test_render_activity(self, rf, post, member):
        context = render_activity(rf.get("/"), member.member, post)
        assert context["object"] == post
        assert context["object_type"] == "post"
        assert context["user"] == member.member
        assert context["community"] == post.community
        assert context["is_content_sensitive"] is False
        assert context["template_name"] == "posts/includes/post.html"

    def test_render_activity_is_pinned(self, rf, post, member):
        context = render_activity(rf.get("/"), member.member, post, is_pinned=True)
        assert context["object"] == post
        assert context["object_type"] == "post"
        assert context["user"] == member.member
        assert context["community"] == post.community
        assert context["is_content_sensitive"] is False
        assert context["template_name"] == "posts/includes/post_pinned.html"

    def test_render_activity_is_detail(self, rf, post, member):
        context = render_activity(rf.get("/"), member.member, post, is_detail=True)
        assert context["object"] == post
        assert context["object_type"] == "post"
        assert context["user"] == member.member
        assert context["community"] == post.community
        assert context["is_content_sensitive"] is False
        assert context["is_detail"] is True
        assert context["template_name"] == "posts/includes/post.html"


class TestGetPinnedActivity:
    def test_get_pinned_activity_if_none(self, member):
        pinned = get_pinned_activity(member.member, member.community)
        assert pinned is None

    def test_get_pinned_activity_if_no_pinned_posts(self, member):
        PostFactory(
            community=member.community, is_pinned=False, published=timezone.now()
        )
        pinned = get_pinned_activity(member.member, member.community)
        assert pinned is None

    def test_get_pinned_activity_if_is_pinned_post(self, member):
        post = PostFactory(
            community=member.community,
            owner=member.member,
            is_pinned=True,
            published=timezone.now(),
        )
        pinned = get_pinned_activity(member.member, member.community)
        assert pinned["pk"] == post.id
        assert pinned["object_type"] == "post"
        assert pinned["object"] == post


class TestIsOembedUrl:
    def test_is_oembed_if_oembed_url_and_user_permitted(self, user_model):
        url = "https://www.youtube.com/watch?v=eLeIJtLebZk"
        user = user_model(show_embedded_content=True)
        assert is_oembed_url(user, url)

    def test_is_oembed_if_oembed_url_and_user_not_permitted(self, user_model):
        url = "https://www.youtube.com/watch?v=eLeIJtLebZk"
        user = user_model(show_embedded_content=False)
        assert not is_oembed_url(user, url)

    def test_is_oembed_if_not_oembed_url(self, user_model):
        url = "https://reddit.com"
        user = user_model(show_embedded_content=True)
        assert not is_oembed_url(user, url)
