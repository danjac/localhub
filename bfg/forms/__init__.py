# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from .fields import CalendarField
from .widgets import CalendarWidget, ClearableImageInput, TypeaheadInput


class FormHelper:
    """Simple class for managing form fieldsets in ModelForms. Fieldsets can be defined
    under the form Meta class or added after form initialization.

    Fieldsets should be defined as pairs of (name, fields)  e.g.

    class MyForm(ModelForm):

        model = MyModel
        fields = (....)
        fieldsets = (
            (None, ("name", "description")),
            ("Preferences", ("field_1", "field_2"))
        )

    Then initiate in your form (or view) as follows:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.form_helper = FormHelper(self)

    Iterating the helper yields the fieldsets (i.e. BoundField instances).
    Any fields not present in the form at the time are ignored:

    for name, fields in form.form_helper:
        print(name, fields)

    """

    def __init__(self, form, fieldsets=None):
        self.form = form
        self.fieldsets = fieldsets or getattr(self.form.Meta, "fieldsets", [])

    def __iter__(self):
        for name, fields in self.fieldsets:
            yield name, [
                self.form[field] for field in fields if field in self.form.fields
            ]


__all__ = [
    "CalendarField",
    "CalendarWidget",
    "ClearableImageInput",
    "FormHelper",
    "TypeaheadInput",
]
