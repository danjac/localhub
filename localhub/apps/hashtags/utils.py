# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse

from localhub.common.utils.text import slugify_unicode


def extract_hashtags(content):
    """Extracts tags (prefixed with "#") in string into a set of tags.
    The extracted tags do not include the hash("#") prefix.

    Args:
        content (str)

    Returns:
        set: valid hashtag strings
    """
    return set(
        [
            hashtag.lower()
            for token in content.split(" ")
            for hashtag in settings.LOCALHUB_HASHTAGS_RE.findall(token)
        ]
    )


def linkify_hashtags(content):
    """Replace all #hashtags in text with links to some tag search page.

    Args:
        content (str)

    Returns:
        str
    """
    tokens = content.split(" ")
    rv = []
    for token in tokens:

        for tag in settings.LOCALHUB_HASHTAGS_RE.findall(token):
            slug = slugify_unicode(tag)
            if slug:
                url = reverse("hashtags:detail", args=[slug])
                token = token.replace("#" + tag, f'<a href="{url}">#{tag}</a>')

        rv.append(token)

    return " ".join(rv)
