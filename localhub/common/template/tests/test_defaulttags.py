# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..defaulttags import active_link, active_link_regex

pytestmark = pytest.mark.django_db


class TestActiveLink:
    def test_no_match(self, rf):
        url = reverse("account_login")
        req = rf.get(url)
        route = active_link({"request": req}, "posts:list")
        assert route.url == reverse("posts:list")
        assert not route.match
        assert not route.exact

    def test_non_exact_match(self, rf, post):
        url = post.get_absolute_url()
        req = rf.get(url)
        route = active_link({"request": req}, "posts:list")
        assert route.url == reverse("posts:list")
        assert route.match
        assert not route.exact

    def test_exact_match(self, rf):
        url = reverse("posts:list")
        req = rf.get(url)
        route = active_link({"request": req}, "posts:list")
        assert route.url == reverse("posts:list")
        assert route.match
        assert route.exact


class TestActiveLinkRegex:
    def test_no_match(self, rf):
        url = reverse("account_login")
        req = rf.get(url)
        route = active_link_regex({"request": req}, "/posts/", "posts:list")
        assert route.url == reverse("posts:list")
        assert not route.match
        assert not route.exact

    def test_non_exact_match(self, rf, post):
        url = post.get_absolute_url()
        req = rf.get(url)
        route = active_link_regex({"request": req}, "/posts/", "posts:list")
        assert route.url == reverse("posts:list")
        assert route.match
        assert not route.exact

    def test_exact_match(self, rf):
        url = reverse("posts:list")
        req = rf.get(url)
        route = active_link_regex({"request": req}, "/posts/", "posts:list")
        assert route.url == reverse("posts:list")
        assert route.match
        assert route.exact


class TestCollapsable:
    def test_if_no_args(self):
        tmpl = template.Template(
            """
        {% collapsable %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({}))
        assert 'data-controller="collapsable"' in rendered

    def test_if_ignore_false(self):
        tmpl = template.Template(
            """
        {% collapsable ignore %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({"ignore": False}))
        assert 'data-controller="collapsable"' in rendered

    def test_if_ignore_true(self):
        tmpl = template.Template(
            """
        {% collapsable ignore %}
        <div>content text</div>
        {% endcollapsable %}
        """
        )
        rendered = tmpl.render(template.Context({"ignore": True}))
        assert 'data-controller="collapsable"' not in rendered
