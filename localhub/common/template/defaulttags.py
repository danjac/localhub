# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import collections
import re

# Django
from django import template
from django.shortcuts import resolve_url

# Localhub
from localhub.common.utils import emojis

register = template.Library()

ActiveLink = collections.namedtuple("Link", "url match exact")


@register.simple_tag(takes_context=True)
def active_link(context, url_name, *args, **kwargs):
    url = resolve_url(url_name, *args, **kwargs)
    if context["request"].path == url:
        return ActiveLink(url, True, True)
    elif context["request"].path.startswith(url):
        return ActiveLink(url, True, False)
    return ActiveLink(url, False, False)


@register.simple_tag(takes_context=True)
def active_link_regex(context, pattern, url_name, *args, **kwargs):
    url = resolve_url(url_name, *args, **kwargs)

    if context["request"].path == url:
        return ActiveLink(url, True, True)

    if re.compile(pattern).match(context["request"].path):
        return ActiveLink(url, True, False)

    return ActiveLink(url, False, False)


@register.simple_tag
def common_emojis():
    """Returns list of commonly used emojis, for use e.g. in markdown widget."""
    return emojis.COMMON_EMOJIS


@register.tag(name="collapsable")
def do_collapsable(parser, token):
    try:
        ignore = template.Variable(token.split_contents()[1])
    except IndexError:
        ignore = False

    nodelist = parser.parse(("endcollapsable",))
    parser.delete_first_token()
    return CollapsableNode(ignore, nodelist)


class CollapsableNode(template.Node):
    def __init__(self, ignore, nodelist):
        self.nodelist = nodelist
        self.ignore = ignore

    def render(self, context):
        content = self.nodelist.render(context)
        if self.ignore:
            try:
                if self.ignore.resolve(context):
                    return content
            except template.VariableDoesNotExist:
                pass
        return template.loader.render_to_string(
            "includes/collapsable.html", {"collapsable_content": content}
        )
