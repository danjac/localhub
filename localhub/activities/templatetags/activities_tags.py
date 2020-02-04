# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from ..utils import get_combined_activity_queryset_count

register = template.Library()


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
