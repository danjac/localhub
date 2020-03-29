# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

import requests
from bs4 import BeautifulSoup

from localhub.utils.http import get_domain, get_response, is_image_url, is_url

logger = logging.getLogger(__name__)


class Opengraph:
    class Invalid(ValueError):
        ...

    @classmethod
    def from_url(cls, url):
        """Grabs OpenGraph and other HTML data from URL and parses
        the HTML content.

        Note that the OpenGraph url value may be different from the
        url in the argument as any redirects are resolved if possible.

        Arguments:
            url {string} -- URL of HTML source page

        Returns:
            OpenGraph -- OpenGraph instance with relevant data.
        """
        try:
            url, response = get_response(url)
        except (requests.RequestException, ValueError) as e:
            raise cls.Invalid(e)

        if not response.ok or "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            raise cls.Invalid("URL does not return valid HTML response")

        return cls(url).parse_html(response.content)

    def __init__(self, url):
        self.url = url
        self.title = None
        self.image = None
        self.description = None
        self.soup = None

    def parse_html(self, html):
        """Parses HTML title, image and description from HTML OpenGraph and
        Twitter meta tags and other HTML content.

        Arguments:
            html {string} -- HTML content

        Returns:
            OpenGraph -- OpenGraph instance
        """
        self.soup = BeautifulSoup(html, "html.parser")
        self.title = self.parse_title_from_html()
        self.image = self.parse_image_from_html()
        self.description = self.parse_description_from_html()
        return self

    def parse_title_from_html(self):
        title = self.parse_meta_tags_from_html("og:title", "twitter:title")
        if title:
            return title
        elif self.soup.h1 and self.soup.h1.text:
            return self.soup.h1.text
        return self.soup.title.string if self.soup.title else get_domain(self.url)

    def parse_image_from_html(self):
        image = self.parse_meta_tags_from_html("og:image", "twitter:image")
        if image and len(image) < 501 and is_url(image) and is_image_url(image):
            return image
        return None

    def parse_description_from_html(self):
        return self.parse_meta_tags_from_html("og:description", "twitter:description")

    def parse_meta_tags_from_html(self, *names):
        for name in names:
            meta = self.soup.find("meta", attrs={"property": name}) or self.soup.find(
                "meta", attrs={"name": name}
            )
            if meta and "content" in meta.attrs:
                return meta.attrs["content"]
        return None
