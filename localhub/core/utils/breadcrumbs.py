# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _


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
