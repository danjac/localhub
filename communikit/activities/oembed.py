# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, Any

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from micawber.providers import Provider
from micawber.providers import bootstrap_oembed as _bootstrap_oembed

from communikit.activities.utils import get_domain


def is_url(s: str) -> bool:
    try:
        URLValidator()(s)
        return True
    except ValidationError:
        return False


def custom_handler(url: str, response_data: Dict[str:Any], **kwargs) -> str:

    title = (
        response_data["title"]
        if is_url(response_data["title"])
        else get_domain(response_data["title"])
    )
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>'  # noqa


custom_extension = {"handler": custom_handler, "urlize_all": False}


def bootstrap_oembed():
    pr = _bootstrap_oembed(cache)
    # add some missing ones e.g. imgur

    pr.register(
        r"https?://gist\.github\.com/\S*",
        Provider("https://github.com/api/oembed"),
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
