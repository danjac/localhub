# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from localhub.users.utils import linkify_mentions
from localhub.utils.urls import is_https

from ..models import (
    get_activity_models,
    get_activity_queryset_count,
    get_activity_querysets,
    load_objects,
)
from ..oembed import bootstrap_oembed
from ..utils import linkify_hashtags

register = template.Library()


_oembed_registry = bootstrap_oembed()


@register.simple_tag
def get_pinned_activity(user, community):
    """
    Returns the single pinned activity for this community.
    """
    if user.is_anonymous or not community.active:
        return None

    qs, querysets = get_activity_querysets(
        lambda model: model.objects.for_community(community)
        .with_common_annotations(user, community)
        .published()
        .exclude_blocked(user)
        .select_related("owner")
        .filter(is_pinned=True)
    )

    result = qs.first()

    if result is None:
        return None

    return load_objects([result], querysets)[0]


@register.simple_tag
def get_draft_count(user, community):
    if user.is_anonymous or not community.active:
        return 0
    return get_activity_queryset_count(
        lambda model: model.objects.for_community(community).drafts(user)
    )


@register.simple_tag
def get_external_draft_count(user, community):
    if user.is_anonymous or not community.active:
        return 0

    return get_activity_queryset_count(
        lambda model: model.objects.filter(
            community__active=True,
            community__membership__active=True,
            community__membership__member=user,
        )
        .exclude(community=community)
        .drafts(user)
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


@register.filter
def strip_external_images(content, user):
    if user.is_authenticated and not user.show_external_images:
        soup = BeautifulSoup(content, "html.parser")
        for img in soup.find_all("img"):
            src = img.attrs.get("src")
            if (
                src
                and not src.startswith(settings.MEDIA_URL)
                and not src.startswith(settings.STATIC_URL)
            ):
                img.decompose()
        return mark_safe(str(soup))
    return content


@register.simple_tag
def resolve_model_url(model, view_name):
    return reverse(f"{model._meta.app_label}:{view_name}")


@register.simple_tag
def resolve_url(activity, view_name):
    return activity.resolve_url(view_name)


@register.simple_tag
def verbose_name(activity):
    return _(activity._meta.verbose_name.capitalize())


@register.simple_tag
def verbose_name_plural(activity):
    return _(activity._meta.verbose_name_plural.capitalize())
