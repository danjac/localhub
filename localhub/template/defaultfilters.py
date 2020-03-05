# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import html

from django import template
from django.utils.safestring import mark_safe

from localhub.utils.urls import (
    REL_SAFE_VALUES,
    get_domain,
    get_domain_url,
    is_https,
    is_image_url,
    is_url,
)

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
    if not is_url(url):
        return url
    if is_image_url(url) and is_https(url):
        html = f'<img src="{url}" alt="{get_domain(url)}">'
        if linkify:
            html = f'<a href="{url}" rel="nofollow">{html}</a>'
        return mark_safe(html)
    return ""


@register.filter
def domain(url):
    """
    Returns domain URL (i.e. minus path)
    """
    return get_domain_url(url) or url


@register.filter
def linkify(url, text=None):
    """
    Creates a "safe" external link to a new tab.
    If text is falsy, uses the URL domain e.g. reddit.com.
    """
    if not is_url(url):
        return url

    text = text or get_domain(url)
    if not text:
        return url

    return mark_safe(
        f'<a href="{url}" rel="{REL_SAFE_VALUES}" target="_blank">{text}</a>'
    )


register.filter(is_image_url)
