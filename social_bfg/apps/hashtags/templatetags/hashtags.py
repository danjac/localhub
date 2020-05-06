# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import template
from django.utils.safestring import mark_safe

from ..utils import linkify_hashtags

register = template.Library()

# rename...
# users_tags -> users
# comments etc


@register.filter(name="linkify_hashtags")
def _linkify_hashtags(content, css_class=None):
    return mark_safe(linkify_hashtags(content))
