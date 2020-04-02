# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.utils.http import URLResolver

from ..factories import PostFactory
from ..forms import PostForm
from ..html_scraper import HTMLScraper

pytestmark = pytest.mark.django_db


@pytest.fixture()
def mock_html_scraper_from_url(mocker):
    scraper = HTMLScraper()
    scraper.title = "Imgur"
    scraper.image = "https://imgur.com/cat.gif"
    scraper.description = "cat"

    mocker.patch(
        "localhub.posts.html_scraper.HTMLScraper.from_url", return_value=scraper
    )
    yield


@pytest.fixture()
def mock_html_scraper_from_invalid_url(mocker):
    mocker.patch(
        "localhub.posts.html_scraper.HTMLScraper.from_url",
        side_effect=HTMLScraper.Invalid,
    )
    yield


class TestPostForm:
    def mock_resolve_url(self, mocker, url):
        mocker.patch(
            "localhub.posts.forms.URLResolver.from_url", return_value=URLResolver(url)
        )

    def test_url_missing(self):

        form = PostForm({"title": "something", "url": "", "description": "test"})

        assert form.is_valid()
        assert form.cleaned_data["title"] == "something"

    def test_title_missing(self, mock_html_scraper_from_url, mocker):

        form = PostForm({"title": "", "url": "http://google.com"})

        self.mock_resolve_url(mocker, form.data["url"])

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "http://google.com"

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

    def test_fetch_opengraph_data_if_url(self, mock_html_scraper_from_url, mocker):
        form = PostForm(
            {"url": "http://twitter.com", "title": "", "fetch_opengraph_data": True}
        )

        self.mock_resolve_url(mocker, form.data["url"])

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "http://twitter.com"
        assert form.cleaned_data["opengraph_image"] == "https://imgur.com/cat.gif"
        assert form.cleaned_data["opengraph_description"] == "cat"

    def test_fetch_opengraph_data_if_url_resolves_differently(
        self, mock_html_scraper_from_url, mocker
    ):
        form = PostForm(
            {"url": "http://twitter.com", "title": "", "fetch_opengraph_data": True}
        )

        self.mock_resolve_url(mocker, "https://twitter.com")

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "https://twitter.com"
        assert form.cleaned_data["opengraph_image"] == "https://imgur.com/cat.gif"
        assert form.cleaned_data["opengraph_description"] == "cat"

    def test_fetch_opengraph_data_if_invalid_url(
        self, mock_html_scraper_from_invalid_url, mocker
    ):
        form = PostForm(
            {"url": "http://twitter.com", "title": "", "fetch_opengraph_data": True}
        )

        self.mock_resolve_url(mocker, form.data["url"])
        assert not form.is_valid()

    def test_fetch_opengraph_data_if_image_url_no_title(
        self, mock_html_scraper_from_url, mocker
    ):
        form = PostForm(
            {
                "url": "http://imgur.com/cat.gif",
                "title": "",
                "fetch_opengraph_data": True,
            }
        )

        self.mock_resolve_url(mocker, form.data["url"])

        assert form.is_valid()
        assert form.cleaned_data["url"] == "http://imgur.com/cat.gif"
        assert form.cleaned_data["title"] == "cat.gif"

    def test_fetch_opengraph_data_if_image_url(
        self, mock_html_scraper_from_url, mocker
    ):
        form = PostForm(
            {
                "url": "http://imgur.com/cat.gif",
                "title": "cat",
                "fetch_opengraph_data": True,
                "opengraph_image": "http://imgur.com/test.jpg",
                "opengraph_description": "test",
            }
        )

        self.mock_resolve_url(mocker, form.data["url"])
        assert form.is_valid()
        assert form.cleaned_data["url"] == "http://imgur.com/cat.gif"
        # selecting image will automatically clear OpenGraph data
        assert form.cleaned_data["opengraph_image"] == ""
        assert form.cleaned_data["opengraph_description"] == ""

    def test_fetch_opengraph_data_if_image_url_resolves_differently(
        self, mock_html_scraper_from_url, mocker
    ):
        form = PostForm(
            {
                "url": "http://imgur.com/cat.gif",
                "title": "cat",
                "fetch_opengraph_data": True,
            }
        )

        self.mock_resolve_url(mocker, "https://imgur.com/cat.gif")

        assert form.is_valid()
        assert form.cleaned_data["url"] == "https://imgur.com/cat.gif"

    def test_fetch_opengraph_data_if_title_and_invalid_url(
        self, mock_html_scraper_from_invalid_url, mocker
    ):
        form = PostForm(
            {"url": "http://twitter.com", "title": "test", "fetch_opengraph_data": True}
        )
        self.mock_resolve_url(mocker, form.data["url"])
        assert not form.is_valid()

    def test_fetch_opengraph_data_if_valid_url_and_no_title(self, mocker):
        form = PostForm(
            {"url": "http://twitter.com", "title": "", "fetch_opengraph_data": True}
        )

        scraper = HTMLScraper()
        scraper.title = None
        scraper.image = "https://imgur.com/cat.gif"
        scraper.description = "cat"

        mocker.patch(
            "localhub.posts.html_scraper.HTMLScraper.from_url", return_value=scraper
        )

        self.mock_resolve_url(mocker, form.data["url"])
        assert not form.is_valid()

    def test_fetch_opengraph_data_if_not_fetch_opengraph_data_from_url(
        self, mock_html_scraper_from_url, mocker
    ):
        form = PostForm(
            {"url": "https://google.com", "title": "", "fetch_opengraph_data": False}
        )

        self.mock_resolve_url(mocker, form.data["url"])

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "https://google.com"
        assert form.cleaned_data["opengraph_image"] == ""
        assert form.cleaned_data["opengraph_description"] == ""

    def test_clear_opengraph_data(self, mock_html_scraper_from_url, mocker):
        post = PostFactory(
            title="Imgur",
            url="https://google.com",
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
        self.mock_resolve_url(mocker, form.data["url"])

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "https://google.com"
        assert form.cleaned_data["opengraph_image"] == ""
        assert form.cleaned_data["opengraph_description"] == ""

    def test_clear_opengraph_data_if_url_resolves_differently(
        self, mock_html_scraper_from_url, mocker
    ):
        post = PostFactory(
            title="Imgur",
            url="http://google.com",
            opengraph_image="http://imgur.com/cat.gif",
            opengraph_description="cat",
        )

        form = PostForm(
            {
                "url": "http://google.com",
                "title": "Imgur",
                "fetch_opengraph_data": False,
                "clear_opengraph_data": True,
            },
            instance=post,
        )
        self.mock_resolve_url(mocker, "https://google.com")

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Imgur"
        assert form.cleaned_data["url"] == "https://google.com"
        assert form.cleaned_data["opengraph_image"] == ""
        assert form.cleaned_data["opengraph_description"] == ""
