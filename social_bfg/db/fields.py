# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.postgres.fields import ArrayField
from django.forms import MultipleChoiceField


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)
