# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.utils.safestring import mark_safe

# Localhub
from localhub.utils import emojis

register = template.Library()


@register.simple_tag
def common_emojis():
    """Returns list of commonly used emojis, for use e.g. in markdown widget.
    """
    return emojis.COMMON_EMOJIS


@register.simple_tag
def svg(name, variant="black", size="24", css_class=None, fill=False):
    """
    """

    if css_class:
        css_classes = [css_class]
    elif variant == "white":
        css_classes = ["text-white"]
    else:
        css_classes = ["text-black"]

    if fill:
        css_classes.append("fill-current")

    return mark_safe(
        template.loader.render_to_string(
            f"includes/svg/{name}.svg.html",
            {"css_class": " ".join(css_classes), "stroke": variant, "size": size},
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
