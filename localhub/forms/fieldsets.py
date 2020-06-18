# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


class FieldSet:
    def __init__(self, form, fields, label=None):
        self.form = form
        self.fields = list(fields)
        self.label = label

    def __iter__(self):
        for field in self.fields:
            if field in self.form.fields:
                yield self.form[field]


class FormHelper:
    def __init__(self, form, *fieldsets):
        self.form = form
        self.fieldsets = list(fieldsets)

    def __iter__(self):
        for label, fields in self.fieldsets:
            yield FieldSet(self.form, fields, label=label)
