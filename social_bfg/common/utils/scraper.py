# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import itertools
import random

# Third Party Libraries
import requests
from bs4 import BeautifulSoup

# Local
from .http import URLResolver, get_domain


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

        return cls(url).scrape(response.content)

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
        self.url = self.get_url() or self.url
        return self

    def get_title(self):
        for value in itertools.chain(
            self.find_meta_tags("og:title", "twitter:title", "parsely-title"),
            self.find_text("h1", "title"),
        ):
            if value:
                return value
        return None

    def get_url(self):
        domain = get_domain(self.url)
        for value in self.find_meta_tags("og:url", "twitter:url", "parsely-link"):
            if value and self.is_acceptable_url(value, domain):
                return value

        return None

    def get_description(self):
        for value in itertools.chain(
            self.find_meta_tags(
                "og:description", "twitter:description", "fb:status", "description",
            ),
            self.find_text("p"),
        ):
            if value:
                return value
        return None

    def get_image(self):
        for value in self.find_meta_tags(
            "og:image", "twitter:image", "parsely-image-url"
        ):
            if self.is_acceptable_image(value):
                return value
        return None

    def find_meta_tags(self, *names):
        for name in names:
            if value := self.find_meta_tag(name):
                yield value

    def find_meta_tag(self, name):
        meta = self.soup.find("meta", attrs={"property": name}) or self.soup.find(
            "meta", attrs={"name": name}
        )
        if meta and "content" in meta.attrs:
            if content := meta.attrs["content"].strip():
                return content
        return None

    def find_text(self, *names):
        for name in names:
            if (
                (tag := self.soup.find(name))
                and tag.text
                and (value := tag.text.strip())
            ):
                yield value

    def is_acceptable_url(self, url, domain):
        # must be a valid URL matching domain of the source URL.
        try:
            resolver = URLResolver.from_url(url)
        except URLResolver.Invalid:
            return False

        return resolver.domain == domain

    def is_acceptable_image(self, image):
        try:
            resolver = URLResolver.from_url(image)
        except URLResolver.Invalid:
            return False
        return resolver.is_image and resolver.is_https
