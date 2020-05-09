# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.utils.safestring import mark_safe

# Social-BFG
from social_bfg.utils import emojis

register = template.Library()


@register.simple_tag
def common_emojis():
    """Returns list of commonly used emojis, for use e.g. in markdown widget.
    """
    return emojis.COMMON_EMOJIS


@register.simple_tag
def svg(name, css_class=""):
    return mark_safe(
        template.loader.render_to_string(
            f"includes/svg/{name}.svg.html", {"css_class": css_class}
        )
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
