# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest

from localhub.utils.scraper import HTMLScraper


@pytest.fixture()
def mock_html_scraper_from_url(mocker):
    scraper = HTMLScraper()
    scraper.title = "Imgur"
    scraper.image = "https://imgur.com/cat.gif"
    scraper.description = "cat"

    mocker.patch("localhub.utils.scraper.HTMLScraper.from_url", return_value=scraper)
    yield


@pytest.fixture()
def mock_html_scraper_from_invalid_url(mocker):
    mocker.patch(
        "localhub.utils.scraper.HTMLScraper.from_url", side_effect=HTMLScraper.Invalid,
    )
    yield
