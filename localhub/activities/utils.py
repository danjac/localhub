# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _

from .models import Activity


def get_activity_models():
    """
    Returns all Activity subclasses
    """
    return Activity.__subclasses__()


def get_combined_activity_queryset(fn, all=False):
    """
    Creates a combined UNION queryset of all Activity subclasses.

    fn should take a model class and return a QuerySet. QuerySets
    for all models should have identical columns.

    Example:

    get_combined_activity_queryset(lambda model: model.objects.only("pk", "title"))
    """
    querysets = [fn(model) for model in get_activity_models()]
    return querysets[0].union(*querysets[1:], all=all)


def get_combined_activity_queryset_count(fn):
    return get_combined_activity_queryset(fn, all=True).count()


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
    current = (
        instance.get_absolute_url(),
        truncatechars(smart_text(instance), 60),
    )
    if instance.published:
        return get_breadcrumbs_for_model(instance.__class__) + [current]
    return [
        (settings.HOME_PAGE_URL, _("Home")),
        (reverse("activities:drafts"), _("Drafts")),
        current,
    ]
