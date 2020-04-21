# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404


class ParentObjectMixin:
    """
    Works like SingleObjectMixin but provides convenient methods
    for fetching a "parent" object.

    This is useful when you want e.g. a form or list view with
    a different "parent" related object to another object

    """

    # if not required, sets parent to None if not found
    parent_required = True

    parent_model = None
    parent_queryset = None
    parent_context_object_name = None
    parent_object_name = "parent"

    parent_pk_field = "pk"
    parent_slug_field = "slug"

    parent_pk_kwarg = "pk"
    parent_slug_kwarg = "slug"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        setattr(self, self.parent_object_name, self.get_parent_object())

    def get_parent_queryset(self):
        if self.parent_model is None and self.parent_queryset is None:
            raise ImproperlyConfigured(
                "parent_model or parent_queryset must be defined"
            )
        if self.parent_queryset is not None:
            return self.parent_queryset

        return self.parent_model.objects.all()

    def get_parent_context_object_name(self):
        return self.parent_context_object_name or self.parent_object_name

    def get_parent_kwargs(self):

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
                queryset or self.get_parent_queryset(), **self.get_parent_kwargs()
            )
        except Http404:
            if self.parent_required:
                raise
            return None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data[self.get_parent_context_object_name()] = getattr(
            self, self.parent_object_name
        )
        return data
