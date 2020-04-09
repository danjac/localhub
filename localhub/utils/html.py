# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import random

import requests
from bs4 import BeautifulSoup

from .http import URLResolver


class HTMLScraper:
    """
    Scrapes HTML content from a page to extract useful data such as title,
    description and image. Prioritizes OpenGraph and other meta data provided
    before parsing actual page body content.
    """

    USER_AGENTS = [
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/57.0.2987.110 "
            "Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.79 "
            "Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) "
            "Gecko/20100101 "
            "Firefox/55.0"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/61.0.3163.91 "
            "Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/62.0.3202.89 "
            "Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/63.0.3239.108 "
            "Safari/537.36"
        ),
    ]

    class Invalid(ValueError):
        ...

    def __init__(self):
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
                url,
                headers={
                    "User-Agent": random.choice(cls.USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}",
                },
                stream=True,
            )
            response.raise_for_status()
            if "text/html" not in response.headers.get("Content-Type", ""):
                raise cls.Invalid("response is not html")
        except requests.RequestException as e:
            raise cls.Invalid(e)

        return cls().scrape(response.content)

    def scrape(self, html):
        """Parses HTML title, image and description from HTML OpenGraph and
        Twitter meta tags and other HTML content.

        Args:
            html (str): HTML content

        Returns:
            HTMLScraper: the instance
        """
        self.soup = BeautifulSoup(html, "html.parser")
        self.title = self.get_title()
        self.image = self.get_image()
        self.description = self.get_description()
        return self

    def get_title(self):
        # priority:
        # OG or twitter title content
        # first <h1> element
        # <title> element
        title = self.find_meta_tag("og:title", "twitter:title")
        if title:
            return title
        if self.soup.h1 and self.soup.h1.text:
            return self.soup.h1.text
        if self.soup.title:
            return self.soup.title.text
        return None

    def get_image(self):
        # priority:
        # OG or twitter image content
        # first <img> element
        image = self.find_meta_tag("og:image", "twitter:image")
        if image and self.is_acceptable_image(image):
            return image

        if self.soup.img:
            image = self.soup.img.attrs.get("src")
            if self.is_acceptable_image(image):
                return image
        return None

    def get_description(self):
        # priority:
        # OG or twitter content
        # first <p> element
        text = self.find_meta_tag(
            "og:description", "twitter:description", "fb:status", "description"
        )
        if text:
            return text
        if self.soup.p:
            return self.soup.p.text
        return None

    def find_meta_tag(self, *names):
        for name in names:
            meta = self.soup.find("meta", attrs={"property": name}) or self.soup.find(
                "meta", attrs={"name": name}
            )
            if meta and "content" in meta.attrs:
                return meta.attrs["content"]
        return None

    def is_acceptable_image(self, image):
        try:
            resolver = URLResolver.from_url(image)
        except URLResolver.Invalid:
            return False
        return resolver.is_image and resolver.is_https
