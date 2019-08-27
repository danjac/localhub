# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests

from bs4 import BeautifulSoup


def fetch_title_from_url(url):
    """
    Fetches title from an HTML page. Returns None
    if unavailable or title not found.
    """
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.title.string if soup.title else None
    return None
