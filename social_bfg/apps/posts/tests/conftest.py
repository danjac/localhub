# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
from social_bfg.utils.http import URLResolver
from social_bfg.utils.scraper import HTMLScraper


@pytest.fixture
def mock_url_resolver(mocker):
    resolver = URLResolver("https://imgur.com")
    mocker.patch("social_bfg.utils.http.URLResolver.from_url", return_value=resolver)


@pytest.fixture
def mock_url_image_resolver(mocker):
    resolver = URLResolver("https://imgur.com/cat.gif")
    mocker.patch("social_bfg.utils.http.URLResolver.from_url", return_value=resolver)


@pytest.fixture()
def mock_html_scraper_from_url(mocker):
    scraper = HTMLScraper()
    scraper.title = "Imgur"
    scraper.image = "https://imgur.com/cat.gif"
    scraper.description = "cat"

    mocker.patch("social_bfg.utils.scraper.HTMLScraper.from_url", return_value=scraper)
    yield


@pytest.fixture()
def mock_html_scraper_from_invalid_url(mocker):
    mocker.patch(
        "social_bfg.utils.scraper.HTMLScraper.from_url",
        side_effect=HTMLScraper.Invalid,
    )
    yield
