# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from localhub.communities.factories import CommunityFactory
from localhub.posts.factories import PostFactory
from localhub.users.factories import UserFactory

from ..templatetags.activities_tags import (
    domain,
    get_draft_count,
    html_unescape,
    is_content_sensitive,
    is_oembed_allowed,
    url_to_img,
)

pytestmark = pytest.mark.django_db


class TestGetDraftCount:
    def test_get_draft_count(self, member):
        PostFactory(
            community=member.community, owner=member.member, published=None
        )
        assert get_draft_count(member.member, member.community) == 1

    def test_get_draft_count_if_anonymous(self, community):
        assert get_draft_count(AnonymousUser(), community) == 0


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


class TestUrlToImg:
    def test_if_image(self):
        url = "http://somedomain.org/test.jpg"
        assert url_to_img(url) == (
            '<a href="http://somedomain.org/test.jpg" rel="nofollow"'
            '><img src="http://somedomain.org/test.jpg" '
            'alt="somedomain.org"></a>'
        )

    def test_if_image_no_link(self):
        url = "http://somedomain.org/test.jpg"
        assert url_to_img(url, False) == (
            '<img src="http://somedomain.org/test.jpg" alt="somedomain.org">'
        )

    def test_if_not_image(self):
        url = "http://somedomain.org/"
        assert url_to_img(url) == ""

    def test_if_not_url(self):
        text = "<div></div>"
        assert url_to_img(text) == "<div></div>"


class TestHtmlUnescape:
    def test_html_unescape(self):
        text = "this is &gt; that"
        assert html_unescape(text) == "this is > that"


class TestIsContentSensitive:
    def test_is_sensitive_anon(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert is_content_sensitive(post, AnonymousUser())

    def test_is_sensitive_auth_ok(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert not is_content_sensitive(
            post, UserFactory(show_sensitive_content=True)
        )

    def test_is_sensitive_auth_not_ok(self):

        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community, description="#nsfw")
        assert is_content_sensitive(
            post, UserFactory(show_sensitive_content=False)
        )

    def test_not_is_sensitive_anon(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not is_content_sensitive(post, AnonymousUser())

    def test_not_is_sensitive_auth(self):
        community = CommunityFactory(content_warning_tags="#nsfw")
        post = PostFactory(community=community)
        assert not is_content_sensitive(
            post, UserFactory(show_sensitive_content=False)
        )


class TestDomain:
    def test_if_not_valid_url(self):
        assert domain("<div />") == "<div />"

    def test_if_valid_url(self):
        assert (
            domain("http://reddit.com")
            == '<a href="http://reddit.com" rel="nofollow">reddit.com</a>'
        )

    def test_if_www(self):
        assert (
            domain("http://www.reddit.com")
            == '<a href="http://www.reddit.com" rel="nofollow">reddit.com</a>'
        )
