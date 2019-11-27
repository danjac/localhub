# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from ..models import Flag

register = template.Library()


@register.simple_tag
def get_flags_count(user, community):
    if not community.active or not user.has_perm(
        "communities.moderate_community", community
    ):
        return 0

    return Flag.objects.filter(community=community).count()
