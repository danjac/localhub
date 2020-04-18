# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.urls import reverse

from localhub.utils.text import slugify_unicode


from .constants import MENTIONS_RE


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


def linkify_mentions(content):
    """
    Replace all @mentions in the text with links to user profile page.
    """

    tokens = content.split(" ")
    rv = []
    for token in tokens:
        for mention in MENTIONS_RE.findall(token):
            url = reverse("users:activities", args=[slugify_unicode(mention)])
            token = token.replace("@" + mention, f'<a href="{url}">@{mention}</a>')

        rv.append(token)

    return " ".join(rv)
