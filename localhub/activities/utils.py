# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import re

from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _

from localhub.utils.text import slugify_unicode

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")


def get_breadcrumbs_for_model(model_cls):
    """
    Returns default breadcrumbs for an Activity model class. Use
    this with BreadcrumbMixin views.
    """
    return [
        (settings.HOME_PAGE_URL, _("Activities")),
        (
            reverse(f"{model_cls._meta.app_label}:list"),
            _(model_cls._meta.verbose_name_plural.title()),
        ),
    ]


def get_breadcrumbs_for_instance(instance):
    """
    Returns default breadcrumbs for an Activity model instance. Use
    this with BreadcrumbMixin views.
    """
    current = (
        instance.get_absolute_url(),
        truncatechars(smart_text(instance), 60),
    )
    if instance.published:
        return get_breadcrumbs_for_model(instance.__class__) + [current]
    return [
        (settings.HOME_PAGE_URL, _("Activities")),
        (reverse("activities:drafts"), _("Drafts")),
        current,
    ]


def extract_hashtags(content):
    """
    Extracts tags (prefixed with "#") in string into a set of tags.
    The extracted tags do not include the hash("#") prefix.
    """
    return set(
        [
            hashtag.lower()
            for token in content.split(" ")
            for hashtag in HASHTAGS_RE.findall(token)
        ]
    )


def linkify_hashtags(content):
    """
    Replace all #hashtags in text with links to some tag search page.
    """
    tokens = content.split(" ")
    rv = []
    for token in tokens:

        for tag in HASHTAGS_RE.findall(token):
            slug = slugify_unicode(tag)
            if slug:
                url = reverse("activities:tag_detail", args=[slug])
                token = token.replace("#" + tag, f'<a href="{url}">#{tag}</a>')

        rv.append(token)

    return " ".join(rv)
