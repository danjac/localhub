# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.urls import reverse
from django.utils import timezone

from localhub.posts.factories import PostFactory
from localhub.posts.models import Post
from localhub.users.factories import UserFactory

from ..templatetags.activities_tags import (
    get_pinned_activity,
    is_oembed_url,
    render_activity,
    resolve_model_url,
    resolve_url,
    strip_external_images,
    verbose_name,
    verbose_name_plural,
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
        assert context["is_detail"] is False
        assert context["template_name"] == "posts/includes/post.html"

    def test_render_activity_is_pinned(self, rf, post, member):
        context = render_activity(rf.get("/"), member.member, post, is_pinned=True)
        assert context["object"] == post
        assert context["object_type"] == "post"
        assert context["user"] == member.member
        assert context["community"] == post.community
        assert context["is_content_sensitive"] is False
        assert context["is_detail"] is False
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


class TestStripExternalImages:
    def test_if_external_image_and_anon_user(self, anonymous_user):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        assert strip_external_images(content, anonymous_user) == content

    def test_if_external_image_and_user_show_external_images(self):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        user = UserFactory(show_external_images=True)
        assert strip_external_images(content, user) == content

    def test_if_external_image_and_not_user_show_external_images(self):
        content = '<p><img src="https://imgur.com/funny.gif"/></p>'
        user = UserFactory(show_external_images=False)
        assert strip_external_images(content, user) == "<p></p>"

    def test_if_internal_image_and_anon_user(self, anonymous_user, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        assert strip_external_images(content, anonymous_user) == content

    def test_if_internal_image_and_user_show_external_images(self, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        user = UserFactory(show_external_images=True)
        assert strip_external_images(content, user) == content

    def test_if_internal_image_and_not_user_show_external_images(self, settings):
        settings.STATIC_URL = "/static/"
        content = '<p><img src="/static/funny.gif"/></p>'
        user = UserFactory(show_external_images=False)
        assert strip_external_images(content, user) == content


class VerboseNameTests:
    def test_verbose_name_of_instance(self, post):
        assert verbose_name(post) == "Post"


class VerboseNamePluralTests:
    def test_verbose_name_of_instance(self, post):
        assert verbose_name_plural(post) == "Posts"

    def test_verbose_name_of_model(self):
        assert verbose_name_plural(Post) == "Posts"


class ResolveUrlTests:
    def test_resolve_url(self, post):
        assert resolve_url(post, "bookmark") == reverse(
            "posts:bookmark", args=[post.id]
        )


class ResolveModelUrlTests:
    def test_resolve_model_url_with_instance(self, post):
        assert resolve_model_url(post, "list") == reverse("posts:list")

    def test_resolve_model_url_with_class(self):
        assert resolve_model_url(Post, "list") == reverse("posts:list")
