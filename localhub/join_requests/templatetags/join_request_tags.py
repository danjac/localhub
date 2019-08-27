# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import template

from localhub.join_requests.models import JoinRequest

register = template.Library()


@register.simple_tag
def get_pending_join_request_count(community):
    """
    Returns total number of pending join requests.
    """
    return JoinRequest.objects.filter(
        status=JoinRequest.STATUS.pending, community=community
    ).count()
