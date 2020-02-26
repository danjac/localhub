# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from localhub.communities.factories import CommunityFactory, MembershipFactory
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

from ..templatetags.activities_tags import (
    get_draft_count,
    get_external_draft_count,
    is_content_sensitive,
    is_oembed_url,
)

pytestmark = pytest.mark.django_db


class TestIsOembedUrl:
    def test_is_oembed_if_oembed_url_and_user_permitted(self):
        url = "https://www.youtube.com/watch?v=eLeIJtLebZk"
        user = get_user_model()(show_embedded_content=True)
        assert is_oembed_url(user, url)

    def test_is_oembed_if_oembed_url_and_user_not_permitted(self):
        url = "https://www.youtube.com/watch?v=eLeIJtLebZk"
        user = get_user_model()(show_embedded_content=False)
        assert not is_oembed_url(user, url)

    def test_is_oembed_if_not_oembed_url(self):
        url = "https://reddit.com"
        user = get_user_model()(show_embedded_content=True)
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
