# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.communities.models import Membership

from ..models import JoinRequest

register = template.Library()


@register.simple_tag
def get_pending_join_request_count(community):
    """
    Returns total number of pending join requests for community.
    """
    return JoinRequest.objects.filter(
        status=JoinRequest.STATUS.pending, community=community
    ).count()


@register.simple_tag(takes_context=True)
def get_pending_local_network_join_request_count(context, user, community):
    """
    Returns total number of pending join requests excluding this community,
    where the current user is an admin.
    """
    context_key = "_join_requests_local_network_count"
    if context_key in context:
        return context[context_key]
    if user.is_anonymous:
        count = 0
    else:
        count = (
            JoinRequest.objects.filter(
                status=JoinRequest.STATUS.pending,
                community__membership__member=user,
                community__membership__active=True,
                community__membership__role=Membership.ROLES.admin,
            )
            .exclude(community=community)
            .distinct()
            .count()
        )
    context[context_key] = count
    return count
