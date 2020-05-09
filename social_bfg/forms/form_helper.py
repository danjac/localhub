# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class Fieldset:
    def __init__(self, form, fields, label=None):
        self.form = form
        self.fields = fields
        self.label = label

    def __iter__(self):
        for field in self.fields:
            if field in self.form.fields:
                yield self.form[field]


class FormHelper:
    """Helper class organizing fieldsets.
    """

    def __init__(self, form, fieldsets=None):
        self.form = form
        self.fieldsets = list(fieldsets or [])

    def __iter__(self):
        for label, fields in self.fieldsets:
            yield Fieldset(self.form, fields, label)
