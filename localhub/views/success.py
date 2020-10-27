# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.views.generic import CreateView, DeleteView, FormView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

# Localhub
from localhub.mixins import SuccessMixin


class SuccessView(SuccessMixin, View):
    """Convenient base class for View with SuccessMixin."""


class SuccessActionView(SingleObjectMixin, SuccessView):
    """Base class for simple AJAX action views (usually POST) with
    standard success response. Automatically loads object at setup.
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()


class SuccessFormView(SuccessMixin, FormView):
    """FormView returning success response with valid form."""

    def form_valid(self, form):
        return self.success_response()


class SuccessCreateView(SuccessMixin, CreateView):
    """CreateView returning success response with valid form."""

    def form_valid(self, form):
        self.object = form.save()
        return self.success_response()


class SuccessUpdateView(SuccessMixin, UpdateView):
    """UpdateView returning success response with valid form."""

    def form_valid(self, form):
        self.object = form.save()
        return self.success_response()


class SuccessDeleteView(SuccessMixin, DeleteView):
    """DeleteView returning success response on execution."""

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.success_response()
