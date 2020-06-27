# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.db import models

# Local
from .forms import HashtagsField as HashtagsFormField
from .utils import extract_hashtags
from .validators import validate_hashtags


class HashtagsProxy(str):
    def extract_hashtags(self):
        return extract_hashtags(self)


class HashtagsFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        value = instance.__dict__[self.field] if instance else None
        if value is None:
            return None
        return HashtagsProxy(value)

    def __set__(self, instance, value):
        instance.__dict__[self.field] = value


class HashtagsField(models.CharField):
    """
    CharField which only permits #tags string. Also
    provides an extract_hashtags method which extracts
    a set of tags.
    """

    default_validators = [validate_hashtags]

    def contribute_to_class(self, cls, name):
        super(HashtagsField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, HashtagsFieldDescriptor(self.name))

    def formfield(self, **kwargs):
        defaults = {
            "form_class": HashtagsFormField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
