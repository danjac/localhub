# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import contextlib

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


@contextlib.contextmanager
def handle_form(request, form_class, **form_kwargs):
    if "_request" in form_kwargs:
        form_kwargs["request"] = form_kwargs.pop("_request")
    if request.method == "POST":
        form = form_class(data=request.POST, files=request.FILES, **form_kwargs)
        yield form, form.is_valid()
    else:
        yield form_class(**form_kwargs), False
