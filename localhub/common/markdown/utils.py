# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Custom Markdown-related functions.
"""

# Standard Library
from functools import partial

# Django
from django.http import Http404
from django.urls import resolve

# Third Party Libraries
import bleach
from bleach import Cleaner  # type: ignore
from bleach.linkifier import TLDS, LinkifyFilter, build_url_re
from markdownx.utils import markdownify as default_markdownify

# Localhub
from localhub.hashtags.utils import linkify_hashtags
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
    "div",
    "span",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
]

ALLOWED_ATTRIBUTES = bleach.ALLOWED_ATTRIBUTES.copy()
ALLOWED_ATTRIBUTES.update(
    {
        "img": ["alt", "src"],
        "a": ["rel", "target", "href", "data-turbo-frame"],
        "span": ["data-typeahead-target"],
    }
)

ADDITIONAL_TLDS = """app audio auto bar bargains best bid bike blog bot
                     car center cern cheap click cloud codes coffee college
                     coop dance data date dating directory download eco
                     education email events exchange faith farm game gay gift
                     global google guru help hiphop hosting house icu info ink
                     international jobs land lgbt life link lol love map market
                     meet menu mobi movie museum music name ngo onl ooo organic
                     party photo photos pics pizzas porn post pro property pub
                     review rocks sale science sex sexy shop social solar store
                     stream sucks support tattoo technology tel today top trade
                     travel ventures video voting webcam wedding wiki win wtf
                     xxx xyz
                  """.split()

URL_RE = build_url_re(TLDS + ADDITIONAL_TLDS)


def external_link_attrs(attrs, new=False):
    # ignore any internal links
    href = attrs.get((None, "href"))
    if href and href.startswith("http"):
        attrs[(None, "target")] = "_blank"
        attrs[(None, "rel")] = "nofollow noopener noreferrer"
    return attrs


def turbo_frame_attrs(attrs, new=False):
    """Re-inserts preview attrs as these otherwise mess up
    markdown pre-rendering"""
    if href := attrs.get((None, "href")):
        try:
            resolve(href)
            attrs[(None, "data-turbo-frame")] = "_top"
        except Http404:
            return attrs
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
    filters=[
        partial(
            LinkifyFilter,
            callbacks=[external_link_attrs, turbo_frame_attrs],
            url_re=URL_RE,
        )
    ],
)
