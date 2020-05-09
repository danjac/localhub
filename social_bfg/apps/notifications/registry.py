# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.exceptions import ImproperlyConfigured

# Local
from .adapter import Adapter


class AdapterRegistry:
    def __init__(self):
        self._registry = {}

    def get_adapter(self, notification):
        """Returns an Adapter instance for this notification.

        The content object Model should be registered at initialization
        using the register() method.

        Args:
            notification: Notification instance

        Returns:
            Adapter subclass

        Raises:
            ImproperlyConfigured: if no Adapter registered for the model
        """
        try:
            return self._registry[notification.content_object.__class__](notification)
        except KeyError:
            raise ImproperlyConfigured(
                "%r does not have a registered notification adapter"
                % self.content_object
            )

    def register(self, adapter_cls, model):
        """Registers the Adapter class with a Model class.

        Args:
            adapter_cls: Adapter subclass
            model: Django Model class

        Returns:
            Adapter subclass

        Raises:
            ImproperlyConfigured: if adapter_cls does not subclass Adapter
        """

        if not issubclass(adapter_cls, Adapter):
            raise ImproperlyConfigured("%r is not an Adapter subclass" % adapter_cls)
        self._registry[model] = adapter_cls
        return adapter_cls


registry = AdapterRegistry()
