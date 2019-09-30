# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.communities.models import Community


register = template.Library()


@register.simple_tag(takes_context=True)
def get_available_community_count(context, user):
    context_key = "_available_community_count"
    if context_key in context:
        return context[context_key]
    if user.is_anonymous:
        count = 0
    else:
        count = Community.objects.listed(user).count()
    context[context_key] = count
    return count
