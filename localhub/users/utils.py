# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.core.exceptions import PermissionDenied
from django.urls import reverse

# Localhub
from localhub.common.utils.text import slugify_unicode

# Local
from .app_settings import MENTIONS_RE


def has_perm_or_403(user, perm, obj=None):
    if not user.has_perm(perm, obj):
        raise PermissionDenied


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
            for mention in MENTIONS_RE.findall(token)
        ]
    )


def linkify_mentions(content, css_class=None):
    """
    Replace all @mentions in the text with links to user profile page.
    """

    tokens = content.split(" ")
    rv = []
    css_class = f' class="{css_class}"' if css_class else ""
    for token in tokens:
        for mention in MENTIONS_RE.findall(token):
            url = reverse("users:activities", args=[slugify_unicode(mention)])
            token = token.replace(
                "@" + mention,
                f'<a href="{url}"{css_class}>@{mention}</a>',
            )

        rv.append(token)

    return " ".join(rv)
