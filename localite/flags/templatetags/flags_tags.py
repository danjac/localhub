# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from localite.core.types import ContextDict
from localite.flags.models import Flag

register = template.Library()


@register.simple_tag(takes_context=True)
def get_flags_count(context: ContextDict) -> int:

    request = context["request"]

    return Flag.objects.filter(community=request.community).count()
