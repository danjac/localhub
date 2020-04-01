# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import pytest
import requests

from ..html_scraper import HTMLScraper


class TestHTMLScraperFromUrl:
    def test_if_non_html_response(self, mocker):
        class MockResponse:
            ok = True
            headers = {"Content-Type": "application/json"}

        mocker.patch(
            "requests.get", return_value=MockResponse,
        )

        with pytest.raises(HTMLScraper.Invalid):
            scraper = HTMLScraper.from_url("http://google.com")
            assert scraper.title is None
            assert scraper.image is None
            assert scraper.description is None

    def test_if_bad_response(self, mocker):
        class MockResponse:
            ok = False

        mocker.patch(
            "requests.get", return_value=MockResponse,
        )

        with pytest.raises(HTMLScraper.Invalid):
            scraper = HTMLScraper.from_url("http://google.com")
            assert scraper.title is None
            assert scraper.image is None
            assert scraper.description is None

    def test_if_request_exception(self, mocker):

        mocker.patch(
            "requests.get", side_effect=requests.RequestException,
        )

        with pytest.raises(HTMLScraper.Invalid):
            scraper = HTMLScraper.from_url("http://google.com")
            assert scraper.title is None
            assert scraper.image is None
            assert scraper.description is None

    def test_title_from_og(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta property="og:title" content="meta title">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.title == "meta title"

    def test_title_from_twitter(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta name="twitter:title" content="meta title">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.title == "meta title"

    def test_title_from_h1(self):
        html = """<html>
        <head>
            <title>page title</title>
        </head>
        <body>
            <h1>PAGE HEADER</h1>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.title == "PAGE HEADER"

    def test_title_from_title_tag(self):
        html = """<html>
        <head>
            <title>page title</title>
        </head>
        </body>
        <body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.title == "page title"

    def test_title_not_found(self):
        html = """<html>
        <head>
        </head>
        </body>
        <body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.title is None

    def test_image_in_meta_property(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta property="og:image" content="http://imgur.com/test.jpg">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.image == "http://imgur.com/test.jpg"

    def test_image_in_meta_name(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta name="og:image" content="http://imgur.com/test.jpg">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.image == "http://imgur.com/test.jpg"

    def test_image_not_in_meta(self):
        html = """<html>
        <head>
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.image is None

    def test_first_image(self):
        html = """<html>
        <head>
        </head>
        <body>
            <img src="https://imgur.com/test.jpg" />
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.image == "https://imgur.com/test.jpg"

    def test_description_in_meta_property(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta property="og:description" content="test">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.description == "test"

    def test_description_in_meta_name(self):
        html = """<html>
        <head>
            <title>page title</title>
            <meta name="og:description" content="test">
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.description == "test"

    def test_description_in_first_para(self):
        html = """<html>
        <head>
            <title>page title</title>
        </head>
        <body>
        <p>this is content</p>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.description == "this is content"

    def test_description_not_in_meta(self):
        html = """<html>
        <head>
            <title>page title</title>
        </head>
        <body>
        </body>
        </html>
        """
        scraper = HTMLScraper().scrape(html)
        assert scraper.description is None
