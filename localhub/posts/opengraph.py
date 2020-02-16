# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings

from localhub.utils.urls import is_image_url, is_url

FAKE_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


IGNORE_FAKE_BROWSER_HEADERS = ("tumblr.com",)


logger = logging.getLogger(__name__)


@dataclass
class Opengraph:
    title: str
    description: str
    image: str


def get_opengraph_from_url(url):
    """
    Given a URL, will try and parse the following data as a tuple:

    title, image, description

    Missing items will be None.

    """
    if not url:
        return Opengraph(None, None, None)

    try:
        response = requests.get(
            url, headers=get_request_headers(url), proxies=get_proxies()
        )
        if not response.ok or "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            raise ValueError("URL does not return valid HTML response")
    except (requests.RequestException, ValueError) as e:
        logger.error("Error fetching response for URL %s: %s", url, e)
        return Opengraph(None, None, None)

    return get_opengraph_from_html(response.content)


def get_opengraph_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    return Opengraph(
        get_title_from_html(soup),
        get_description_from_html(soup),
        get_image_from_html(soup),
    )


def get_title_from_html(soup):
    if title := get_meta_content(soup, "og:title", "twitter:title"):
        return title
    return soup.title.string if soup.title else None


def get_image_from_html(soup):
    image = get_meta_content(soup, "og:image", "twitter:image")
    if image and len(image) < 501 and is_url(image) and is_image_url(image):
        return image
    return None


def get_description_from_html(soup):
    return get_meta_content(soup, "og:description", "twitter:description")


def get_meta_content(soup, *names):
    for name in names:
        meta = soup.find("meta", attrs={"property": name}) or soup.find(
            "meta", attrs={"name": name}
        )
        if meta and "content" in meta.attrs:
            return meta.attrs["content"]
    return None


def get_request_headers(url):
    netloc = urlparse(url).netloc
    for domain in IGNORE_FAKE_BROWSER_HEADERS:
        if netloc.endswith(domain):
            return {}
    return {"User-Agent": FAKE_BROWSER_USER_AGENT}


def get_proxies():
    if settings.OPENGRAPH_PROXY_URL:
        return {
            "http": settings.OPENGRAPH_PROXY_URL,
            "https": settings.OPENGRAPH_PROXY_URL,
        }
    return {}
