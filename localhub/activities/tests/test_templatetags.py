# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.utils import timezone

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.posts.factories import PostFactory
from localhub.posts.models import Post
from localhub.users.factories import UserFactory

from ..templatetags.activities_tags import (
    get_draft_count,
    get_external_draft_count,
    get_pinned_activity,
    is_content_sensitive,
    is_oembed_url,
    resolve_model_url,
    resolve_url,
    strip_external_images,
    verbose_name,
    verbose_name_plural,
)

pytestmark = pytest.mark.django_db


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


class TestGetDraftCount:
    def test_get_draft_count(self, member):
        PostFactory(community=member.community, owner=member.member, published=None)
        assert get_draft_count(member.member, member.community) == 1

    def test_get_draft_count_if_anonymous(self, community):
        assert get_draft_count(AnonymousUser(), community) == 0


class TestGetLocalNetworkDraftCount:
    def test_get_external_draft_count(self, member):
        PostFactory(community=member.community, owner=member.member, published=None)
        other = CommunityFactory()
        MembershipFactory(member=member.member, community=other)
        PostFactory(community=other, owner=member.member, published=None)
        assert get_external_draft_count(member.member, member.community) == 1

    def test_get_external_draft_count_if_anonymous(self, community):
        assert get_external_draft_count(AnonymousUser(), community) == 0


class TestIsContentSensitive:
    def test_is_sensitive_anon(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert is_content_sensitive(post, AnonymousUser())

    def test_is_sensitive_auth_ok(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert not is_content_sensitive(post, UserFactory(show_sensitive_content=True))

    def test_is_sensitive_auth_not_ok(self):

        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert is_content_sensitive(post, UserFactory(show_sensitive_content=False))

    def test_not_is_sensitive_anon(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not is_content_sensitive(post, AnonymousUser())

    def test_not_is_sensitive_auth(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not is_content_sensitive(post, UserFactory(show_sensitive_content=False))


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
