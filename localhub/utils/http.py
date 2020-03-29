# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import requests
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_urlvalidator = URLValidator()

FAKE_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


IGNORE_FAKE_BROWSER_HEADERS = ("tumblr.com",)


REL_SAFE_VALUES = "nofollow noopener noreferrer"

IMAGE_EXTENSIONS = (
    "bmp",
    "gif",
    "gifv",
    "jpeg",
    "jpg",
    "pjpeg",
    "png",
    "svg",
    "tif",
    "tiff",
    "webp",
)


def is_https(url):
    return url and urlparse(url).scheme == "https"


def is_url(url):
    """
    Checks if a value is a valid URL.
    """

    if url is None:
        return False
    try:
        _urlvalidator(url)
    except ValidationError:
        return False
    return True


def is_image_url(url):
    _, ext = os.path.splitext(urlparse(url).path.lower())
    return ext[1:] in IMAGE_EXTENSIONS


def get_domain_url(url):
    """
    Returns the root domain URL minus path etc.
    """

    if not is_url(url):
        return url

    parts = urlparse(url)
    return parts.scheme + "://" + parts.netloc


def clean_domain(domain):
    """
    Removes www. segment of a domain.
    """
    if domain and domain.startswith("www."):
        return domain[4:]
    return domain


def get_domain(url):
    """Returns domain of URL e.g. https://google.com -> google.com

    Arguments:
        url {string or None}

    Returns:
        string or None -- original argument if URL not valid, otherwise domain.
    """
    if not is_url(url):
        return url

    return clean_domain(urlparse(url).netloc)


def get_response(url):
    """Fetches a response handling redirects and proxies using HTTP GET.

    Arguments:
        url {string} -- valid URL

    Raises:
        requests.RequestException

    Returns:
        Tuple[string, requests.Response] -- final redirected URL and response object.
    """
    try:
        # see if redirect in HEAD
        response = requests.head(url, allow_redirects=True)
        if response.ok and response.url:
            url = response.url
    except (requests.RequestException):
        # ignore and continue
        pass

    response = requests.get(
        url, headers=get_request_headers(url), proxies=get_proxies()
    )
    return url, response


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
