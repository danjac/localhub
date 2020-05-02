# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from .fields import CalendarField
from .widgets import CalendarWidget, ClearableImageInput, TypeaheadInput


class FormHelper:
    """Simple class for managing more complex forms e.g. fieldsets.
    """

    fieldsets = []

    def __init__(self, form):
        self.form = form

    def __iter__(self):
        for name, fields in self.fieldsets:
            yield (
                name,
                [self.form[field] for field in fields if field in self.form.fields],
            )


__all__ = [
    "CalendarField",
    "CalendarWidget",
    "ClearableImageInput",
    "TypeaheadInput",
    "FormHelper",
]
