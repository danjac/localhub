# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import json

# Django
from django.conf import settings
from django.core.cache import cache

# Third Party Libraries
from micawber.providers import Provider
from micawber.providers import bootstrap_oembed as _bootstrap_oembed


def bootstrap_oembed():
    """
    Adds some more Providers to Micawber's default oembed list.
    """
    try:
        pr = _bootstrap_oembed(cache)
    except json.JSONDecodeError:
        return None
    # add some missing ones e.g. imgur

    pr.register(
        r"https?://gist\.github\.com/\S*", Provider("https://github.com/api/oembed"),
    )
    pr.register(
        r"https?://\S*imgur\.com/\S+", Provider("https://api.imgur.com/oembed")
    ),

    # Wordpress requires a "for" parameter pointing to current site domain

    wp_provider = Provider("http://public-api.wordpress.com/oembed/")
    try:
        host = settings.ALLOWED_HOSTS[0]
    except IndexError:
        host = "localhost"
    wp_provider.base_params.update({"for": host, "as_article": "true"})

    pr.register(r"https://\S+\.wordpress\.com/\S+", wp_provider)

    return pr
