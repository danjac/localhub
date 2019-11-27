# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from localhub.communities.models import Membership

from ..models import Flag

register = template.Library()


@register.simple_tag
def get_flag_count(user, community):
    if not community.active or not user.has_perm(
        "communities.moderate_community", community
    ):
        return 0

    return Flag.objects.filter(community=community).count()


@register.simple_tag
def get_local_network_flag_count(user, community):
    if user.is_anonymous or not community.active:
        return 0
    return (
        Flag.objects.filter(
            community__active=True,
            community__membership__member=user,
            community__membership__active=True,
            community__membership__role__in=(
                Membership.ROLES.moderator,
                Membership.ROLES.admin,
            ),
        )
        .exclude(community=community)
        .count()
    )
