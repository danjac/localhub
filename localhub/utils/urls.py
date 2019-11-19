# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

_urlvalidator = URLValidator()

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


def get_domain(url):
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """

    if url is None or not is_url(url):
        return None

    if (domain := urlparse(url).netloc).startswith("www."):
        domain = domain[4:]
    return domain
