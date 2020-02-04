# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

register = template.Library()


@register.simple_tag
def is_post_oembed(user, post):
    return user.is_authenticated and user.show_embedded_content and post.is_oembed()
