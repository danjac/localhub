# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings

from communikit.core.types import ContextDict

register = template.Library()


@register.inclusion_tag("users/includes/avatar.html")
def avatar(
    user: settings.AUTH_USER_MODEL, avatar_class: str = "avatar-sm"
) -> ContextDict:

    if user.name:
        initials = "".join([n[0].upper() for n in user.name.split()][:2])
    else:
        initials = user.username[0].upper()

    return {"user": user, "avatar_class": avatar_class, "initials": initials}
