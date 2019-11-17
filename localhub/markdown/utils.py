# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom Markdown-related functions.
"""

import re

import bleach
from bleach import Cleaner  # type: ignore
from bleach.linkifier import LinkifyFilter
from django.urls import reverse
from markdownx.utils import markdownify as default_markdownify

from ..utils.text import slugify_unicode

ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "p",
    "pre",
]

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update({"img": ["alt", "src"]})

cleaner = Cleaner(
    tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, filters=[LinkifyFilter]
)

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")
MENTIONS_RE = re.compile(r"(?:^|\s)[＠ @]{1}([^\s#<>!.?[\]|{}]+)")


def markdownify(content):
    """
    Drop-in replacement to default MarkdownX markdownify function.

    - Linkifies URLs, @mentions and #hashtags
    - Restricts permitted HTML tags to safer subset

    """
    return cleaner.clean(
        default_markdownify(linkify_hashtags(linkify_mentions(content)))
    )


def extract_mentions(content):
    """
    Returns set of @mentions in text
    """
    return set(
        [
            mention
            for token in content.split(" ")
            for mention in MENTIONS_RE.findall(token)
        ]
    )


def linkify_mentions(content):
    """
    Replace all @mentions in the text with links to user profile page.
    """

    tokens = content.split(" ")
    rv = []
    for token in tokens:
        for mention in MENTIONS_RE.findall(token):
            url = reverse("users:activities", args=[slugify_unicode(mention)])
            token = token.replace("@" + mention, f'<a href="{url}">@{mention}</a>')

        rv.append(token)

    return " ".join(rv)


def extract_hashtags(content):
    """
    Extracts tags (prefixed with "#") in string into a set of tags.
    The extracted tags do not include the hash("#") prefix.
    """
    return set(
        [
            hashtag.lower()
            for token in content.split(" ")
            for hashtag in HASHTAGS_RE.findall(token)
        ]
    )


def linkify_hashtags(content):
    """
    Replace all #hashtags in text with links to some tag search page.
    """
    tokens = content.split(" ")
    rv = []
    for token in tokens:

        for tag in HASHTAGS_RE.findall(token):
            slug = slugify_unicode(tag)
            if slug:
                url = reverse("activities:tag_detail", args=[slug])
                token = token.replace("#" + tag, f'<a href="{url}">#{tag}</a>')

        rv.append(token)

    return " ".join(rv)
