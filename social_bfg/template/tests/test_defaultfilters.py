# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import forms
from django.urls import NoReverseMatch, reverse

# Third Party Libraries
import pytest

# Social-BFG
from social_bfg.apps.posts.models import Post

from ..defaultfilters import (
    contains,
    from_dictkey,
    html_unescape,
    is_multipart,
    lazify,
    linkify,
    resolve_url,
    url_to_img,
    verbose_name,
    verbose_name_plural,
)

pytestmark = pytest.mark.django_db


class IsMultipartTests:
    def test_form_with_no_file_fields(self):
        class MyForm(forms.Form):
            name = forms.CharField(max_length=200)

        form = MyForm()
        assert not is_multipart(form)

    def test_form_with_with_file_fields(self):
        class MyForm(forms.Form):
            name = forms.CharField(max_length=200)
            logo = forms.ImageField()

        form = MyForm()
        assert is_multipart(form)


class ResolveUrlTests:
    def test_resolve_url_with_instance(self, post):
        assert resolve_url(post, "bookmark") == reverse(
            "posts:bookmark", args=[post.id]
        )

    def test_resolve_url_with_instance_if_no_args(self, post):
        assert resolve_url(post, "list") == reverse("posts:list", args=[])

    def test_resolve_url_with_class(self, post):
        assert resolve_url(Post, "list") == reverse("posts:list", args=[])

    def test_resolve_url_if_no_match(self, post):
        with pytest.raises(NoReverseMatch):
            resolve_url(post, "unknown")


class VerboseNameTests:
    def test_verbose_name_of_instance(self, post):
        assert verbose_name(post) == "post"


class VerboseNamePluralTests:
    def test_verbose_name_of_instance(self, post):
        assert verbose_name_plural(post) == "posts"

    def test_verbose_name_of_model(self):
        assert verbose_name_plural(Post) == "posts"


class TestContains:
    def test_if_collection_is_none(self):
        assert contains(None, "x") is False

    def test_if_collection_does_contain(self):
        assert contains(["x"], "x")

    def test_if_collection_does_not_contain(self):
        assert not contains(["y"], "x")


class TestLazify:
    def test_if_image(self):
        text = """this is an image <img src="test.jpg" />"""
        assert 'loading="lazy"' in lazify(text)

    def test_if_iframe(self):
        text = """this is an image <iframe src="test.jpg" />"""
        assert 'loading="lazy"' in lazify(text)


class TestUrlToImg:
    def test_if_image(self):
        url = "https://somedomain.org/test.jpg"
        assert url_to_img(url) == (
            '<a href="https://somedomain.org/test.jpg" rel="nofollow noopener noreferrer"'
            ' target="_blank"><img src="https://somedomain.org/test.jpg" alt="test.jpg"></a>'
        )

    def test_if_unsafe_image(self):
        url = "http://somedomain.org/test.jpg"
        assert url_to_img(url) == ""

    def test_if_image_no_link(self):
        url = "https://somedomain.org/test.jpg"
        assert url_to_img(url, False) == (
            '<img src="https://somedomain.org/test.jpg" alt="test.jpg">'
        )

    def test_if_not_image(self):
        url = "https://somedomain.org/"
        assert url_to_img(url) == ""

    def test_if_not_url(self):
        text = "<div></div>"
        assert url_to_img(text) == "<div></div>"


class TestHtmlUnescape:
    def test_html_unescape(self):
        text = "this is &gt; that"
        assert html_unescape(text) == "this is > that"


class TestLinkify:
    def test_if_not_valid_url(self):
        assert linkify("<div />") == "<div />"

    def test_if_valid_url(self):
        assert linkify("http://reddit.com").endswith(">reddit.com</a>")

    def test_if_www(self):
        assert linkify("http://www.reddit.com").endswith(">reddit.com</a>")

    def test_if_text(self):
        assert linkify("http://reddit.com", "REDDIT").endswith(">REDDIT</a>")


class TestFromDictkey:
    def test_is_dict(self):
        d = {"1": "3"}

        assert from_dictkey(d, "1") == "3"

    def test_is_none(self):
        assert from_dictkey(None, "1") is None
