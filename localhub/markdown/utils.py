# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom Markdown-related functions.
"""

from functools import partial

import bleach
from bleach import Cleaner  # type: ignore
from bleach.linkifier import LinkifyFilter
from markdownx.utils import markdownify as default_markdownify

from localhub.activities.utils import linkify_hashtags
from localhub.users.utils import linkify_mentions

ALLOWED_TAGS = bleach.ALLOWED_TAGS + [
    "abbr",
    "br",
    "code",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "p",
    "pre",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
]

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update({"img": ["alt", "src"], "a": ["rel", "target", "href"]})


def set_link_target(attrs, new=False):
    # ignore any internal links
    href = attrs.get((None, "href"))
    if href and href.startswith("http"):
        attrs[(None, "target")] = "_blank"
        attrs[(None, "rel")] = "nofollow noopener noreferrer"
    return attrs


def markdownify(content):
    """
    Drop-in replacement to default MarkdownX markdownify function.

    - Linkifies URLs, @mentions and #hashtags
    - Restricts permitted HTML tags to safer subset

    """
    return cleaner.clean(
        default_markdownify(linkify_hashtags(linkify_mentions(content)))
    )


cleaner = Cleaner(
    tags=ALLOWED_TAGS,
    attributes=ALLOWED_ATTRIBUTES,
    filters=[partial(LinkifyFilter, callbacks=[set_link_target])],
)
