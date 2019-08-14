# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


_urlvalidator = URLValidator()


def is_url(url: Optional[str]) -> bool:

    if url is None:
        return False
    try:
        _urlvalidator(url)
    except ValidationError:
        return False
    return True


def get_domain(url: Optional[str]) -> Optional[str]:
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """

    if url is None or not is_url(url):
        return None

    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain
