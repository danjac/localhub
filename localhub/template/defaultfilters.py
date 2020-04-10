# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import html

from bs4 import BeautifulSoup
from django import template
from django.utils.safestring import mark_safe

from localhub.utils.http import URLResolver, get_root_url, is_image_url

register = template.Library()


@register.filter
def from_dictkey(dct, key, default=None):
    """
    Returns value from a dict.
    """
    return dict(dct or {}).get(key, default)


@register.filter
def html_unescape(text):
    """
    Removes any html entities from the text.
    """
    return html.unescape(text)


@register.filter
def url_to_img(url, linkify=True):
    """
    Given a URL, tries to render the <img> tag. Returns text as-is
    if not an image, returns empty string if plain URL.

    Only https links are permitted.
    """
    try:
        resolver = URLResolver.from_url(url)
    except URLResolver.Invalid:
        return url
    if resolver.is_image and resolver.is_https:
        html = f'<img src="{resolver.url}" alt="{resolver.filename}">'
        if linkify:
            return _external_link(resolver.url, html)
        return mark_safe(html)
    return ""


@register.filter
def domain(url):
    """
    Returns domain URL (i.e. minus path)
    """
    return get_root_url(url)


@register.filter
def linkify(url, text=None):
    """
    Creates a "safe" external link to a new tab.
    If text is falsy, uses the URL domain e.g. reddit.com.
    """
    try:
        resolver = URLResolver.from_url(url)
    except URLResolver.Invalid:
        return url

    text = text or resolver.domain
    if not text:
        return url

    return _external_link(url, text)


register.filter(is_image_url)


@register.filter
def lazify(text):
    """
    Adds "loading"="lazy" to any img or iframe tags in the content.
    """
    if not text:
        return text
    soup = BeautifulSoup(text, "html.parser")
    for element in soup.find_all(["iframe", "img"]):
        element["loading"] = "lazy"
    return mark_safe(str(soup))


def _external_link(url, text):
    return mark_safe(
        f'<a href="{url}" rel="nofollow noopener noreferrer" target="_blank">{text}</a>'
    )
