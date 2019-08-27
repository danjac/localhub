# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from localhub.users.utils import user_display

register = template.Library()


@register.inclusion_tag("users/includes/avatar.html")
def avatar(user, avatar_class="avatar-sm"):
    """
    Displays the avatar if any for a given user. If no image available
    will render initials (based on name/username)
    """

    initials = "".join([n[0].upper() for n in user_display(user).split()][:2])

    return {"user": user, "avatar_class": avatar_class, "initials": initials}
