# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Local
from .fields import CalendarField
from .fieldsets import FormHelper
from .widgets import CalendarWidget, ClearableImageInput, TypeaheadInput

__all__ = [
    "CalendarField",
    "CalendarWidget",
    "ClearableImageInput",
    "FormHelper",
    "TypeaheadInput",
]


class FormProcess:
    def __init__(self, request, form_class, form_kwargs):
        self.request = request
        self.form_class = form_class
        self.form_kwargs = form_kwargs

    def __enter__(self):
        if self.request.method == "POST":
            form = self.form_class(
                data=self.request.POST, files=self.request.FILES, **self.form_kwargs
            )
            return form, form.is_valid()
        return self.form_class(**self.form_kwargs), False

    def __exit__(self, *args, **kwargs):
        ...


def process_form(request, form_class, **form_kwargs):
    return FormProcess(request, form_class, form_kwargs)
