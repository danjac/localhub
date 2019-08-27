# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.db import models

from localhub.core.markdown.fields import MarkdownField


class MarkdownFieldMixin:
    """
    This strips out the custom HTML form rendering for the
    Markdown form field, as it is not compatible with the
    Django admin. Instead we just use a plain TEXTAREA.
    """

    model: models.Model

    def get_form(self, request, obj, **kwargs):
        """
        formfield_overrides doesn't work with MarkdownField
        """
        form = super().get_form(request, obj, **kwargs)
        for field in self.model._meta.fields:
            if isinstance(field, MarkdownField):
                form.base_fields[field.name].widget = forms.Textarea()
        return form
