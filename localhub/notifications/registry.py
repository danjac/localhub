# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured

from .adapters import Adapter


class AdapterRegistry:
    def __init__(self):
        self._registry = {}

    def get_adapter(self, notification):
        """Returns an Adapter instance for this notification.

        The content object Model should be registered at initialization
        using the register() method.

        Arguments:
            notification {Notification} -- Notification instance

        Raises:
            ImproperlyConfigured: if no Adapter registered for the model

        Returns:
            Adapter -- an Adapter subclass
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

        Arguments:
            adapter_cls {Adapter} -- Adapter subclass
            model {Model} -- Django Model class

        Raises:
            ImproperlyConfigured: if adapter_cls does not subclass Adapter

        Returns:
            Adapter subclass
        """

        if not issubclass(adapter_cls, Adapter):
            raise ImproperlyConfigured("%r is not an Adapter subclass" % adapter_cls)
        self._registry[model] = adapter_cls
        return adapter_cls


registry = AdapterRegistry()
