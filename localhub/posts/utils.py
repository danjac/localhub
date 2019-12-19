# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from bs4 import BeautifulSoup

from localhub.utils.urls import is_image_url, is_url

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


def fetch_metadata_from_url(url):
    """
    Given a URL, will try and fetch the following data as a tuple:

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

    soup = BeautifulSoup(response.content, "html.parser")

    title = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
        "meta", attrs={"name": "twitter:title"}
    )

    if title and "content" in title.attrs:
        title = title["content"]
    else:
        title = soup.title.string if soup.title else None

    image = None

    try:
        image = soup.find("meta", attrs={"property": "og:image"}).attrs[
            "content"
        ]
        if len(image) < 501 and is_url(image) and is_image_url(image):
            image = image
    except (AttributeError, KeyError):
        pass

    description = soup.find(
        "meta", attrs={"property": "og:description"}
    ) or soup.find("meta", attrs={"name": "twitter:description"})
    if description and "content" in description.attrs:
        description = description.attrs["content"]
    else:
        description = None

    return title, image, description
