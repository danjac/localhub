# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.http import HttpResponseRedirect
from django.utils.functional import cached_property
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

# Local
from .success import (
    SuccessActionView,
    SuccessCreateView,
    SuccessDeleteView,
    SuccessFormView,
    SuccessUpdateView,
    SuccessView,
)


class ActionView(SingleObjectMixin, View):
    """Handles a simple POST action on an object"""

    success_url = None

    def get_success_url(self):
        return self.success_url or self.object.get_absolute_url()

    @cached_property
    def object(self):
        return self.get_object()

    def render_to_response(self):
        return HttpResponseRedirect(self.get_success_url())


__all__ = [
    "SuccessActionView",
    "SuccessCreateView",
    "SuccessDeleteView",
    "SuccessFormView",
    "SuccessView",
    "SuccessUpdateView",
]
