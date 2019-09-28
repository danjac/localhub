# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from django.contrib.auth.models import AnonymousUser

from localhub.activities.templatetags.activities_tags import (
    domain,
    html_unescape,
    is_content_sensitive,
    url_to_img,
)
from localhub.communities.tests.factories import CommunityFactory
from localhub.posts.tests.factories import PostFactory
from localhub.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


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
        assert url_to_img(url) == url

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
