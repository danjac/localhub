# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from bs4 import BeautifulSoup

from localhub.utils.http import get_domain, is_image_url, is_url


class HTMLScraper:
    """
    Scrapes HTML content from a page to extract useful data such as title,
    description and image. Prioritizes OpenGraph and other meta data provided
    before parsing actual page body content.
    """

    FAKE_BROWSER_USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    )

    IGNORE_FAKE_BROWSER_HEADERS = ("tumblr.com",)

    class Invalid(ValueError):
        ...

    def __init__(self, url):
        self.url = url
        self.title = None
        self.image = None
        self.description = None
        self.soup = None

    @classmethod
    def from_url(cls, url):
        """Grabs OpenGraph, Twitter and other HTML data from URL and parses
        the HTML content.

        Args:
            url (string): URL of HTML source page

        Returns:
            HTMLScraper: HTMLScraper instance with relevant data.

        Raises:
            HTMLScraper.Invalid: if unreachable URL or data returned not HTML
        """
        try:
            response = requests.get(
                url, headers={"User-Agent": cls.FAKE_BROWSER_USER_AGENT}
            )
        except requests.RequestException as e:
            raise cls.Invalid(e)

        if not response.ok or "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            raise cls.Invalid("URL does not return valid HTML response")

        return cls(url).parse_html(response.content)

    def parse_html(self, html):
        """Parses HTML title, image and description from HTML OpenGraph and
        Twitter meta tags and other HTML content.

        Args:
            html (str): HTML content

        Returns:
            HTMLScraper: the instance
        """
        self.soup = BeautifulSoup(html, "html.parser")
        self.title = self.title_from_html()
        self.image = self.image_from_html()
        self.description = self.description_from_html()
        return self

    def title_from_html(self):
        # priority:
        # OG or twitter title content
        # first <h1> element
        # <title> element
        title = self.meta_tags_from_html("og:title", "twitter:title")
        if title:
            return title
        elif self.soup.h1 and self.soup.h1.text:
            return self.soup.h1.text
        return self.soup.title.string if self.soup.title else get_domain(self.url)

    def image_from_html(self):
        # priority:
        # OG or twitter image content
        # first <img> element
        image = self.meta_tags_from_html("og:image", "twitter:image")
        if not image and self.soup.img:
            image = self.soup.img.attrs.get("src")
        if self.is_acceptable_image(image):
            return image
        return None

    def description_from_html(self):
        # priority:
        # OG or twitter content
        # first <p> element
        text = self.meta_tags_from_html(
            "og:description", "twitter:description", "fb:status", "description"
        )
        if not text and self.soup.p:
            text = self.soup.p.string
        return text or None

    def meta_tags_from_html(self, *names):
        for name in names:
            meta = self.soup.find("meta", attrs={"property": name}) or self.soup.find(
                "meta", attrs={"name": name}
            )
            if meta and "content" in meta.attrs:
                return meta.attrs["content"]
        return None

    def is_acceptable_image(self, image):
        return image and len(image) < 501 and is_url(image) and is_image_url(image)
