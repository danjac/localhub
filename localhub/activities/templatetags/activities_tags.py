# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import html

from django import template
from django.utils.safestring import mark_safe

from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.polls.models import Poll
from localhub.posts.models import Post
from localhub.utils.urls import get_domain, is_image_url, is_url

register = template.Library()


@register.simple_tag
def get_draft_count(user, community):
    if user.is_anonymous or not community.active:
        return 0
    querysets = [
        model.objects.for_community(community).drafts(user).only("pk")
        for model in (Post, Event, Photo, Poll)
    ]
    return querysets[0].union(*querysets[1:], all=True).count()


@register.simple_tag(takes_context=True)
def is_oembed_allowed(context, user):
    if not context["request"].do_not_track:
        return True

    if user.is_authenticated and user.show_embedded_content:
        return True

    return False


@register.filter
def is_content_sensitive(activity, user):
    if user.is_authenticated and user.show_sensitive_content:
        return False
    return bool(activity.get_content_warning_tags())


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

    <a href="http://reddit.com">reddit.com</a>
    """
    domain = get_domain(url)
    if domain:
        return mark_safe(f'<a href="{url}" rel="nofollow">{domain}</a>')
    return url
