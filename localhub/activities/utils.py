# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import os

from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import gettext as _

from unidecode import unidecode


_urlvalidator = URLValidator()

IMAGE_EXTENSIONS = (
    "bmp",
    "gif",
    "gifv",
    "jpeg",
    "jpg",
    "pjpeg",
    "png",
    "svg",
    "tif",
    "tiff",
    "webp",
)


def is_url(url):
    """
    Checks if a value is a valid URL.
    """

    if url is None:
        return False
    try:
        _urlvalidator(url)
    except ValidationError:
        return False
    return True


def is_image_url(url):
    _, ext = os.path.splitext(urlparse(url).path.lower())
    return ext[1:] in IMAGE_EXTENSIONS


def get_domain(url):
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """

    if url is None or not is_url(url):
        return None

    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def get_breadcrumbs_for_model(model_cls):
    """
    Returns default breadcrumbs for an Activity model class. Use
    this with BreadcrumbMixin views.
    """
    return [
        (settings.HOME_PAGE_URL, _("Home")),
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
    return get_breadcrumbs_for_model(instance.__class__) + [
        (instance.get_absolute_url(), truncatechars(smart_text(instance), 60))
    ]


def slugify_unicode(text):
    """
    Slugify to ASCII attempting to render any Unicode text.
    """
    return slugify(unidecode(smart_text(text)), allow_unicode=False)
