# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from ..factories import PostFactory
from ..forms import PostForm
from ..opengraph import Opengraph

pytestmark = pytest.mark.django_db


class TestPostForm:
    def test_url_missing(self):

        form = PostForm({"title": "something", "url": "", "description": "test"})

        assert form.is_valid()

    def test_title_missing(self):

        form = PostForm({"title": "", "url": "http://google.com"})

        assert form.is_valid()

    def test_title_and_url_both_missing(self):

        form = PostForm({"title": "", "url": "", "description": ""})

        assert not form.is_valid()

    def test_opengraph_data_present(self):
        post = PostFactory(
            opengraph_image="http://imgur.com/cat.gif", opengraph_description="cat"
        )
        form = PostForm(instance=post)
        assert form.initial["fetch_opengraph_data"] is False
        assert "clear_opengraph_data" in form.fields

    def test_opengraph_data_not_present(self, post):
        form = PostForm(instance=post)
        assert "clear_opengraph_data" not in form.fields

    def test_fetch_opengraph_data_if_url(self, mocker):
        def mock_fetch(url):
            og = Opengraph("https://imgur.com")
            og.title = "Imgur"
            og.image = "https://imgur.com/cat.gif"
            og.description = "cat"
            return og

        mocker.patch("localhub.posts.opengraph.Opengraph.from_url", mock_fetch)

        form = PostForm(
            {"url": "https://google.com", "title": "", "fetch_opengraph_data": True}
        )

        assert form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["title"] == "Imgur"
        assert cleaned_data["opengraph_image"] == "https://imgur.com/cat.gif"
        assert cleaned_data["opengraph_description"] == "cat"

    def test_fetch_opengraph_data_if_not_fetch_opengraph_data_from_url(self, mocker):
        def mock_fetch(url):
            og = Opengraph("https://imgur.com")
            og.title = "Imgur"
            og.image = "https://imgur.com/cat.gif"
            og.description = "cat"
            return og

        mocker.patch("localhub.posts.opengraph.Opengraph.from_url", mock_fetch)

        form = PostForm(
            {"url": "https://google.com", "title": "", "fetch_opengraph_data": False}
        )

        assert form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["title"] == "Imgur"
        assert cleaned_data["opengraph_image"] == ""
        assert cleaned_data["opengraph_description"] == ""

    def test_clear_opengraph_data(self, mocker):
        post = PostFactory(
            title="Imgur",
            opengraph_image="http://imgur.com/cat.gif",
            opengraph_description="cat",
        )

        form = PostForm(
            {
                "url": "https://google.com",
                "title": "Imgur",
                "fetch_opengraph_data": False,
                "clear_opengraph_data": True,
            },
            instance=post,
        )

        assert form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["title"] == "Imgur"
        assert cleaned_data["opengraph_image"] == ""
        assert cleaned_data["opengraph_description"] == ""
