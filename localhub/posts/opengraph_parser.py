# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from bs4 import BeautifulSoup

from localhub.utils.urls import is_image_url, is_url

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


def parse_opengraph_data_from_url(url):
    """
    Given a URL, will try and parse the following data as a tuple:

    title, image, description

    Missing items will be None.

    """
    if not url:
        return (None, None, None)

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        if not response.ok or "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            raise ValueError
    except (requests.RequestException, ValueError):
        return (None, None, None)

    return parse_opengraph_data_from_html(response.content)


def parse_opengraph_data_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    return (
        _parse_title_from_html(soup),
        _parse_image_from_html(soup),
        _parse_description_from_html(soup),
    )


def _parse_title_from_html(soup):
    title = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
        "meta", attrs={"name": "twitter:title"}
    )
    if title and "content" in title.attrs:
        return title["content"]
    return soup.title.string if soup.title else None


def _parse_image_from_html(soup):
    try:
        image = soup.find("meta", attrs={"property": "og:image"}).attrs["content"]
        if len(image) < 501 and is_url(image) and is_image_url(image):
            return image
    except (AttributeError, KeyError):
        pass

    return None


def _parse_description_from_html(soup):
    description = soup.find("meta", attrs={"property": "og:description"}) or soup.find(
        "meta", attrs={"name": "twitter:description"}
    )
    if description and "content" in description.attrs:
        return description.attrs["content"]
    return None
