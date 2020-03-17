# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import ImproperlyConfigured

from .adapters import Adapter


class AdapterRegistry:
    def __init__(self):
        self._registry = {}

    def get_adapter(self, notification):
        try:
            return self._registry[notification.content_object.__class__](notification)
        except KeyError:
            raise ImproperlyConfigured(
                "%r does not have a registered notification adapter"
                % self.content_object
            )

    def register(self, adapter_cls, model):
        if not issubclass(adapter_cls, Adapter):
            raise ImproperlyConfigured("%r is not an Adapter subclass" % adapter_cls)
        self._registry[model] = adapter_cls
        return adapter_cls


registry = AdapterRegistry()
