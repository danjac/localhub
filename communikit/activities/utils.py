# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Optional

from urllib.parse import urlparse


def get_domain(url: str) -> Optional[str]:
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """
    if not url:
        return None
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain
