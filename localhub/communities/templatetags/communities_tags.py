# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from ..models import Community

register = template.Library()


@register.simple_tag
def get_visible_community_count(user):
    """
    Returns number of communities visible to this user
    """
    if user.is_anonymous:
        return 0
    return Community.objects.visible(user).count()
