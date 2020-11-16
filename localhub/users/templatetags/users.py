# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import template
from django.conf import settings
from django.template.base import token_kwargs
from django.utils.safestring import mark_safe

# Third Party Libraries
from bs4 import BeautifulSoup

# Local
from ..utils import linkify_mentions

register = template.Library()


@register.inclusion_tag("users/includes/avatar.html")
def avatar(user, size=16, css_class=""):
    """Displays the avatar if any for a given user."""
    return {
        "user": user,
        "size": str(size),
        "css_class": css_class,
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
            values = {"user": user, "notice": notice}
            values.update(
                {
                    key: value.resolve(context)
                    for key, value in self.extra_context.items()
                }
            )
            with context.push(**values):
                dismissable_content = mark_safe(self.nodelist.render(context))
                context["dismissable_content"] = dismissable_content
                return template.loader.render_to_string(
                    self.template, context.flatten()
                )

        return ""


@register.filter(name="linkify_mentions")
def _linkify_mentions(content, css_class=None):
    return mark_safe(linkify_mentions(content, css_class))


@register.filter
def strip_external_images(content, user):
    """If user has disabled external images then removes
    any such <img> tags from the content. Images under
    MEDIA_URL or STATIC_URL should be kept.

    Args:
        content (str)
        user (User)

    Returns:
        str: content minus any external images.
    """
    if user.is_authenticated and not user.show_external_images:
        soup = BeautifulSoup(content, "html.parser")
        for img in soup.find_all("img"):
            src = img.attrs.get("src")
            if (
                src
                and not src.startswith(settings.MEDIA_URL)
                and not src.startswith(settings.STATIC_URL)
            ):
                img.decompose()
        return mark_safe(str(soup))
    return content
