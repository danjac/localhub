# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.communities.models import Membership

from ..models import JoinRequest

register = template.Library()


@register.simple_tag
def get_pending_join_request_count(user, community):
    """
    Returns total number of pending join requests for community.
    """
    if not community.active or not user.has_perm(
        "communities.manage_community", community
    ):
        return 0

    return JoinRequest.objects.filter(
        status=JoinRequest.Status.PENDING, community=community
    ).count()


@register.simple_tag
def get_pending_external_join_request_count(user, community):
    """
    Returns total number of pending join requests excluding this community,
    where the current user is an admin.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        JoinRequest.objects.filter(
            status=JoinRequest.Status.PENDING,
            community__membership__member=user,
            community__membership__active=True,
            community__membership__role=Membership.Role.ADMIN,
        )
        .exclude(community=community)
        .distinct()
        .count()
    )
