# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property


class ParentObjectMixin:
    """
    Works SingleObjectMixin but provides convenient methods
    for fetching a "parent" object.
    """

    # sets parent to None if not found
    parent_optional = False

    parent_model = None
    parent_queryset = None
    parent_context_object_name = None

    parent_pk_field = "pk"
    parent_slug_field = "slug"

    parent_pk_kwarg = "pk"
    parent_slug_kwarg = "slug"

    @cached_property
    def parent(self):
        return self.get_parent_object()

    def get_parent_queryset(self):
        if self.parent_model is None and self.parent_queryset is None:
            raise ImproperlyConfigured(
                "parent_model or parent_queryset must be defined"
            )
        if self.parent_queryset is not None:
            return self.parent_queryset

        return self.parent_model.objects.all()

    def get_parent_context_object_name(self):
        if self.parent_context_object_name is not None:
            return self.parent_context_object_name
        return self.parent._meta.model_name

    def get_parent_url_kwargs(self):

        kwargs = {}

        if self.parent_pk_kwarg in self.kwargs:
            kwargs[self.parent_pk_field] = self.kwargs[self.parent_pk_kwarg]

        elif self.parent_slug_kwarg in self.kwargs:
            kwargs[self.parent_slug_field] = self.kwargs[self.parent_slug_kwarg]

        else:
            raise Http404()

        return kwargs

    def get_parent_object(self, queryset=None):
        try:
            return get_object_or_404(
                queryset or self.get_parent_queryset(), **self.get_kwargs()
            )
        except Http404:
            if self.parent_optional:
                return None
            raise

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data[self.get_parent_context_object_name()] = self.parent
        return data
