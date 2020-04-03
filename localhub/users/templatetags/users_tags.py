# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

register = template.Library()


@register.inclusion_tag("users/includes/avatar.html")
def avatar(user, avatar_class="avatar-sm"):
    """
    Displays the avatar if any for a given user. If no image available
    will render initials (based on name/username)
    """

    initials = "".join([n[0].upper() for n in user.get_display_name().split()][:2])

    return {"user": user, "avatar_class": avatar_class, "initials": initials}
