# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.utils.translation import gettext as _


class ParentObjectMixin:
    """
    Works like SingleObjectMixin but provides convenient methods
    for fetching a "parent" object.

    This is useful when you want e.g. a form or list view with
    a different "parent" related object to another object
    """

    # if not required, sets parent to None if not found
    parent_required = True

    parent_context_object_name = None
    parent_object_name = "parent"
    parent_model = None

    parent_pk_field = "pk"
    parent_slug_field = "slug"

    parent_pk_kwarg = "pk"
    parent_slug_kwarg = "slug"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        setattr(self, self.parent_object_name, self.get_parent_object())

    def get_parent_queryset(self):
        """Returns the parent queryset.

        Returns:
            QuerySet
        """
        if self.parent_model is None:
            raise ImproperlyConfigured(
                "You must define parent_model or override get_parent_queryset()."
            )

        return self.parent_model.objects.all()

    def get_parent_context_object_name(self):
        """Context name used in template."""
        return self.parent_context_object_name or self.parent_object_name

    def get_parent_kwargs(self):
        """Returns PK and slug kwargs in the URL. If neither present then
        raises a 404.

        Returns:
            dict

        Raises:
            Http404: if pk or slug field are missing.
        """

        kwargs = {}

        if self.parent_pk_kwarg in self.kwargs:
            kwargs[self.parent_pk_field] = self.kwargs[self.parent_pk_kwarg]

        elif self.parent_slug_kwarg in self.kwargs:
            kwargs[self.parent_slug_field] = self.kwargs[self.parent_slug_kwarg]

        else:
            raise Http404()

        return kwargs

    def get_parent_object(self, queryset=None):
        """Fetches the parent object. If parent_required is True and object is not
        None, then raises Http 404. Otherwise returns None.

        Args:
            queryset (QuerySet, optional): QuerySet. Otherwise calls get_parent_queryset()

        Returns:
            Model

        Raises:
            Http404: if parent not found and parent_required is True
        """
        queryset = queryset or self.get_parent_queryset()
        try:
            return queryset.get(**self.get_parent_kwargs())
        except queryset.model.DoesNotExist:
            if self.parent_required:
                raise Http404(
                    _("No %(object_name)s found")
                    % {"object_name": queryset.model._meta.model_name}
                )
            return None

    def get_context_data(self, **kwargs):
        """Includes parent_context_object_name in context data.
        """
        data = super().get_context_data(**kwargs)
        data[self.get_parent_context_object_name()] = getattr(
            self, self.parent_object_name
        )
        return data
