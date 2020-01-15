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
    get_local_network_draft_count,
    is_content_sensitive,
    is_oembed_allowed,
)

pytestmark = pytest.mark.django_db


class TestGetDraftCount:
    def test_get_draft_count(self, member):
        PostFactory(community=member.community, owner=member.member, published=None)
        assert get_draft_count(member.member, member.community) == 1

    def test_get_draft_count_if_anonymous(self, community):
        assert get_draft_count(AnonymousUser(), community) == 0


class TestGetLocalNetworkDraftCount:
    def test_get_local_network_draft_count(self, member):
        PostFactory(community=member.community, owner=member.member, published=None)
        other = CommunityFactory()
        MembershipFactory(member=member.member, community=other)
        PostFactory(community=other, owner=member.member, published=None)
        assert get_local_network_draft_count(member.member, member.community) == 1

    def test_get_local_network_draft_count_if_anonymous(self, community):
        assert get_local_network_draft_count(AnonymousUser(), community) == 0


class TestIsOembedAllowed:
    def test_if_does_track(self, rf):
        req = rf.get("/")
        req.do_not_track = False
        assert is_oembed_allowed(
            {"request": req}, get_user_model()(show_embedded_content=False)
        )

    def test_if_anonymous(self, rf):
        req = rf.get("/")
        req.do_not_track = True
        assert not is_oembed_allowed({"request": req}, AnonymousUser())

    def test_if_user_allows(self, rf):
        req = rf.get("/")
        req.do_not_track = True
        user = get_user_model()(show_embedded_content=True)
        assert is_oembed_allowed({"request": req}, user)

    def test_if_user_not_allows(self, rf):
        req = rf.get("/")
        req.do_not_track = True
        user = get_user_model()(show_embedded_content=False)
        assert not is_oembed_allowed({"request": req}, user)


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
