# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from ..models import Invite

register = template.Library()


@register.simple_tag
def get_pending_invite_count(user):
    """
    Returns count of pending invites to this user.
    """
    if user.is_anonymous:
        return 0
    return Invite.objects.pending().for_user(user).count()
