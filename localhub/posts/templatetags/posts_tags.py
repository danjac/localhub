# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from localhub.activities.templatetags.activities_tags import is_oembed_allowed

register = template.Library()


@register.simple_tag(takes_context=True)
def is_post_oembed(context, user, post):
    return is_oembed_allowed(context, user) and post.is_oembed()
