# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SuccessMixin:
    """Provides defaults for success message and redirect URL.
    """

    def get_success_message(self, success_message=None, object=None, model=None):
        """Returns success message string. Interpolates
        object and model verbose name as "object" and "model"
        respectively.

        Args:
            success_message(str, optional): a message string. If not provided
                then class should define success_message attribute.
                (default: None)
            object (Model, optional): Django Model instance. If None then
                self.object is assumed. (default: None)
            model (Model class, optional). Django Model class. If None then
                either object (see above) or self.model are assumed. (default: None)

        Returns:
            str

        Raises:
            ImproperlyConfigured: if no success_message is defined in the class
                or as argument.
        """
        success_message = success_message or getattr(self, "success_message", None)

        if success_message is None:
            raise ImproperlyConfigured(
                "You must define success_message for this class, "
                "pass success_message as argument, or or override "
                "get_success_message"
            )

        object = object or getattr(self, "object", None)
        model = model or object or getattr(self, "model", None)

        dct = {}

        if object:
            dct["object"] = object
        if model:
            dct["model"] = model._meta.verbose_name.title()

        return success_message % dct

    def get_success_url(self, object=None):
        """Returns redirect URL.

        Args:
            object: object instance. If None then assumes self.object. Must be provided
                if success_url is not defined.

        Returns:
            str

        Raises:
            ImproperlyConfigured: if no object or success_url is defined.
        """
        success_url = getattr(self, "success_url", None)
        if success_url:
            return self.success_url
        object = object or getattr(self, "object", None)
        if object is None:
            raise ImproperlyConfigured(
                "You must either define success_url or object, or pass object as argument"
            )
        return object.get_absolute_url()
