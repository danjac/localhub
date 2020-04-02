# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import html

from django import template
from django.utils.safestring import mark_safe

from localhub.utils.http import REL_SAFE_VALUES, URLResolver, is_image_url, get_root_url

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
    resolver = URLResolver(url)
    if not resolver.is_valid:
        return url
    if resolver.is_image and resolver.is_https:
        html = f'<img src="{resolver.url}" alt="{resolver.filename}">'
        if linkify:
            html = f'<a href="{resolver.url}" rel="nofollow">{html}</a>'
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
    resolver = URLResolver(url)
    if not resolver.is_valid:
        return url

    text = text or resolver.domain
    if not text:
        return url

    return mark_safe(
        f'<a href="{url}" rel="{REL_SAFE_VALUES}" target="_blank">{text}</a>'
    )


register.filter(is_image_url)
