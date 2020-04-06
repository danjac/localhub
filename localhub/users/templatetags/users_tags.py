# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.template.base import token_kwargs
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("users/includes/avatar.html")
def avatar(user, avatar_class="avatar-sm"):
    """
    Displays the avatar if any for a given user. If no image available
    will render initials (based on name/username)
    """

    initials = "".join([n[0].upper() for n in user.get_display_name().split()][:2])

    return {"user": user, "avatar_class": avatar_class, "initials": initials}


@register.inclusion_tag("users/includes/dismissable_notice.html")
def dismissable_notice(user, notice, text, css_class=None):
    show_notice = user.is_anonymous or notice not in user.dismissed_notices
    return {
        "user": user,
        "notice": notice,
        "dismissable_content": text,
        "css_class": css_class,
        "show_notice": show_notice,
    }


@register.tag
def dismissable(parser, token):
    """
    Renders a notice dismissable by the user.

    Example:

    {% dismissable user "private-stash" "toast-primary" %}
    my notice content goes here...
    {% enddismissable %}
    """
    bits = token.split_contents()[1:]

    try:
        user, notice = bits[:2]
    except ValueError:
        raise template.TemplateSyntaxError("user and notice must be provided")

    extra_context = token_kwargs(bits[2:], parser)

    nodelist = parser.parse(("enddismissable",))
    parser.delete_first_token()

    return DismissableNode(user, notice, nodelist, extra_context=extra_context)


class DismissableNode(template.Node):
    template = "users/includes/dismissable_notice.html"

    def __init__(self, user, notice, nodelist, extra_context=None):

        self.user = template.Variable(user)
        self.notice = template.Variable(notice)
        self.extra_context = extra_context or {}
        self.nodelist = nodelist

    def render(self, context):

        user = self.user.resolve(context)
        notice = self.notice.resolve(context)

        show_notice = user.is_anonymous or notice not in user.dismissed_notices

        if show_notice:
            context.update({"user": user, "notice": notice})
            context.push(
                {
                    key: value.resolve(context)
                    for key, value in self.extra_context.items()
                }
            )
            dismissable_content = mark_safe(self.nodelist.render(context))
            context.update(
                {
                    "dismissable_content": dismissable_content,
                    "show_notice": True,  # TBD: remove
                }
            )
            return template.loader.render_to_string(self.template, context.flatten())

        return ""
