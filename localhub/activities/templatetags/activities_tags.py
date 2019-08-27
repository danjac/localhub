# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import mimetypes

from urllib.parse import urlparse

from django import template
from django.utils.safestring import mark_safe

from localhub.activities.utils import get_domain, is_url

register = template.Library()

IMAGE_TYPES = ("image/jpeg", "image/png", "image/gif")


@register.filter
def is_content_sensitive(activity, user):
    if user.is_authenticated and user.show_sensitive_content:
        return False
    return bool(activity.get_content_warning_tags())


@register.filter
def url_to_img(url, linkify=True):
    """
    Given a URL, tries to render the <img> tag. Returns URL unparsed
    if not an image.
    """
    if url is None or not is_url(url):
        return url
    mimetype, _ = mimetypes.guess_type(urlparse(url).path)
    if mimetype in IMAGE_TYPES:
        html = f'<img src="{url}" alt="{get_domain(url)}">'
        if linkify:
            html = f'<a href="{url}" rel="nofollow">{html}</a>'
        return mark_safe(html)
    return url


@register.filter
def domain(url):
    """
    Shows a linked URL domain e.g. if http://reddit.com:

    <a href="http://reddit.com">reddit.com</a>
    """
    domain = get_domain(url)
    if domain:
        return mark_safe(f'<a href="{url}" rel="nofollow">{domain}</a>')
    return url
