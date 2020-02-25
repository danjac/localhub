# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template
from django.utils.safestring import mark_safe

from localhub.markdown.utils import linkify_hashtags, linkify_mentions
from localhub.utils.urls import is_https

from ..oembed import bootstrap_oembed
from ..utils import get_combined_activity_queryset_count

register = template.Library()


_oembed_registry = bootstrap_oembed()


@register.simple_tag
def get_draft_count(user, community):
    if user.is_anonymous or not community.active:
        return 0
    return get_combined_activity_queryset_count(
        lambda model: model.objects.for_community(community).drafts(user).only("pk")
    )


@register.simple_tag
def get_local_network_draft_count(user, community):
    if user.is_anonymous or not community.active:
        return 0

    return get_combined_activity_queryset_count(
        lambda model: model.objects.filter(
            community__active=True,
            community__membership__active=True,
            community__membership__member=user,
        )
        .exclude(community=community)
        .drafts(user)
        .only("pk")
    )


@register.filter
def is_content_sensitive(activity, user):
    if user.is_authenticated and user.show_sensitive_content:
        return False
    return bool(activity.get_content_warning_tags())


@register.filter
def is_oembed_url(user, url):
    if (
        not url
        or not is_https(url)
        or not user.is_authenticated
        or not user.show_embedded_content
    ):
        return False
    return _oembed_registry.provider_for_url(url) is not None


@register.filter(name="linkify_mentions")
def _linkify_mentions(content):
    return mark_safe(linkify_mentions(content))


@register.filter(name="linkify_hashtags")
def _linkify_hashtags(content):
    return mark_safe(linkify_hashtags(content))
