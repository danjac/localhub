# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import html

from django import template
from django.utils.safestring import mark_safe

from localhub.utils.urls import REL_SAFE_VALUES, get_domain, is_image_url, is_url

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
    """
    if url is None or not is_url(url):
        return url
    if is_image_url(url):
        html = f'<img src="{url}" alt="{get_domain(url)}">'
        if linkify:
            html = f'<a href="{url}" rel="nofollow">{html}</a>'
        return mark_safe(html)
    return ""


@register.filter
def domain(url):
    """
    Shows a linked URL domain e.g. if http://reddit.com:

    <a href="http://reddit.com" ...>reddit.com</a>
    """
    domain = get_domain(url)
    if domain:
        return mark_safe(
            f'<a href="{url}" rel="{REL_SAFE_VALUES}" target="_blank">{domain}</a>'
        )
    return url
