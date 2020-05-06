# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.utils.safestring import mark_safe

# Social-BFG
from social_bfg.utils import emojis
from social_bfg.utils.http import URLResolver

register = template.Library()


@register.simple_tag
def common_emojis():
    """Returns list of commonly used emojis, for use e.g. in markdown widget.
    """
    return emojis.COMMON_EMOJIS


@register.simple_tag
def external_link(url, text, css_class=""):
    try:
        resolver = URLResolver.from_url(url)
    except URLResolver.Invalid:
        return url

    text = text or resolver.domain
    if not text:
        return url

    css_class = f' class="{css_class}"' or ""
    return mark_safe(
        f'<a href="{url}" rel="nofollow noopener noreferrer" target="_blank"{css_class}>{text}</a>'
    )


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
