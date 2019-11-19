# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.template.decorators import with_cached_context_value

from ..models import Community

register = template.Library()


@register.simple_tag(takes_context=True)
@with_cached_context_value
def get_available_community_count(context, user):
    if user.is_anonymous:
        return 0
    return Community.objects.listed(user).count()
