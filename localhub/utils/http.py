# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_urlvalidator = URLValidator()


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
