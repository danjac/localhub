# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings

# Social-BFG
from social_bfg.utils.text import slugify_unicode

# from django.urls import reverse


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
            for hashtag in settings.SOCIAL_BFG_HASHTAGS_RE.findall(token)
        ]
    )


def linkify_hashtags(content, css_class=None):
    """Replace all #hashtags in text with links to some tag search page.

    Args:
        content (str)

    Returns:
        str
    """
    tokens = content.split(" ")
    rv = []
    css_class = f' class="{css_class}"' if css_class else ""
    for token in tokens:

        for tag in settings.SOCIAL_BFG_HASHTAGS_RE.findall(token):
            slug = slugify_unicode(tag)
            if slug:
                url = f"/tags/{slug}/"  # reverse("hashtags:detail", args=[slug])
                token = token.replace(
                    "#" + tag, f'<a href="{url}"{css_class}>#{tag}</a>'
                )

        rv.append(token)

    return " ".join(rv)
