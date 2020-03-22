# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.communities.models import Membership

from ..models import JoinRequest

register = template.Library()


@register.simple_tag
def get_sent_join_request_count(user):
    """
    Returns total number of pending join requests sent
    by this user for all communities
    """
    if not user.is_authenticated:
        return 0

    return JoinRequest.objects.for_sender(user).count()


@register.simple_tag
def get_pending_join_request_count(user, community):
    """
    Returns total number of pending join requests for community.
    """
    if not community.active or not user.has_perm(
        "communities.manage_community", community
    ):
        return 0

    return JoinRequest.objects.for_community(community).pending().count()


@register.simple_tag
def get_pending_external_join_request_count(user, community):
    """
    Returns total number of pending join requests excluding this community,
    where the current user is an admin.
    """
    if user.is_anonymous or not community.active:
        return 0
    return (
        JoinRequest.objects.pending()
        .filter(
            community__membership__member=user,
            community__membership__active=True,
            community__membership__role=Membership.Role.ADMIN,
        )
        .exclude(community=community)
        .distinct()
        .count()
    )
