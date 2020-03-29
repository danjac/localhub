# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from localhub.utils.http import get_domain, is_image_url, is_url, resolve_url


class Opengraph:

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
    def get_response(cls, url):
        url = resolve_url(url)
        response = requests.get(
            url, headers=cls.get_headers(url), proxies=cls.get_proxies()
        )
        return url, response

    @classmethod
    def get_headers(cls, url):
        netloc = urlparse(url).netloc
        for domain in cls.IGNORE_FAKE_BROWSER_HEADERS:
            if netloc.endswith(domain):
                return {}
        return {"User-Agent": cls.FAKE_BROWSER_USER_AGENT}

    @classmethod
    def get_proxies(cls):
        if settings.OPENGRAPH_PROXY_URL:
            return {
                "http": settings.OPENGRAPH_PROXY_URL,
                "https": settings.OPENGRAPH_PROXY_URL,
            }
        return {}

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
            url, response = cls.get_response(url)
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

        Arguments:
            html {string} -- HTML content

        Returns:
            OpenGraph -- OpenGraph instance
        """
        self.soup = BeautifulSoup(html, "html.parser")
        self.title = self.title_from_html()
        self.image = self.image_from_html()
        self.description = self.description_from_html()
        return self

    def title_from_html(self):
        title = self.meta_tags_from_html("og:title", "twitter:title")
        if title:
            return title
        elif self.soup.h1 and self.soup.h1.text:
            return self.soup.h1.text
        return self.soup.title.string if self.soup.title else get_domain(self.url)

    def image_from_html(self):
        image = self.meta_tags_from_html("og:image", "twitter:image")
        if image and len(image) < 501 and is_url(image) and is_image_url(image):
            return image
        return None

    def description_from_html(self):
        return self.meta_tags_from_html("og:description", "twitter:description")

    def meta_tags_from_html(self, *names):
        for name in names:
            meta = self.soup.find("meta", attrs={"property": name}) or self.soup.find(
                "meta", attrs={"name": name}
            )
            if meta and "content" in meta.attrs:
                return meta.attrs["content"]
        return None
