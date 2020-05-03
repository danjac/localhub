# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.db import models

from .forms import MentionsField as MentionsFormField
from .utils import extract_mentions
from .validators import validate_mentions


class MentionsProxy(str):
    def extract_mentions(self):
        return extract_mentions(self)


class MentionsFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        value = instance.__dict__[self.field] if instance else None
        if value is None:
            return None
        return MentionsProxy(value)

    def __set__(self, instance, value):
        instance.__dict__[self.field] = value


class MentionsField(models.CharField):
    """
    CharField which only permits @mentions string. Also
    provides an extract_mentions method which extracts
    a set of tags.
    """

    default_validators = [validate_mentions]

    def contribute_to_class(self, cls, name):
        super(MentionsField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, MentionsFieldDescriptor(self.name))

    def formfield(self, **kwargs):
        defaults = {
            "form_class": MentionsFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
