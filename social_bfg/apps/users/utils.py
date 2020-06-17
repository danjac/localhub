# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.conf import settings
from django.urls import reverse

# Social-BFG
from social_bfg.utils.text import slugify_unicode


def user_display(user):
    """
    Returns default rendering of a user. Used with the
    django_allauth user_display template tag.
    """
    return user.get_display_name()


def extract_mentions(content):
    """
    Returns set of @mentions in text
    """
    return set(
        [
            mention
            for token in content.split(" ")
            for mention in settings.SOCIAL_BFG_MENTIONS_RE.findall(token)
        ]
    )


def linkify_mentions(content, css_class=None, with_hovercard_attrs=True):
    """
    Replace all @mentions in the text with links to user profile page.
    """

    tokens = content.split(" ")
    rv = []
    css_class = f' class="{css_class}"' if css_class else ""
    for token in tokens:
        for mention in settings.SOCIAL_BFG_MENTIONS_RE.findall(token):
            username = slugify_unicode(mention)
            url = reverse("users:activities", args=[username])
            hovercard_url = reverse("users:hovercard", args=[username])
            actions = (
                'data-action="mouseenter->hovercard#show mouseleave->hovercard#hide"'
            )
            hovercard_attrs = f'data-controller="hovercard" data-hovercard-url={hovercard_url} {actions} '
            start = "<a " + (hovercard_attrs if with_hovercard_attrs else "")
            token = token.replace(
                "@" + mention,
                f'{start}href="{url}"{css_class}>@{mention}<span data-target="hovercard.container"></span></a>',
            )

        rv.append(token)

    return " ".join(rv)
