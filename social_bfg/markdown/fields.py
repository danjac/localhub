# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


"""
Custom functionality for the Markdownx field.

This provides additional methods on the field:

- obj.description.markdown() -> returns safe HTML string
- obj.description.extract_mentions() -> returns set of "@" mention strings
- obj.description.extract_hashtags() -> returns set of "#" tag strings
"""

from django.template.defaultfilters import striptags
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from social_bfg.apps.hashtags.utils import extract_hashtags
from social_bfg.apps.users.utils import extract_mentions

from .utils import markdownify
from .widget import TypeaheadMarkdownWidget


class MarkdownProxy(str):
    def markdown(self):
        return mark_safe(markdownify(self))

    def extract_mentions(self):
        return extract_mentions(self)

    def extract_hashtags(self):
        return extract_hashtags(self)

    def plaintext(self):
        return striptags(self.markdown()).strip()


class MarkdownFieldDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        value = instance.__dict__[self.field] if instance else None
        if value is None:
            return None
        return MarkdownProxy(value)

    def __set__(self, instance, value):
        instance.__dict__[self.field] = value


class MarkdownField(MarkdownxField):
    def contribute_to_class(self, cls, name):
        super(MarkdownField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, MarkdownFieldDescriptor(self.name))

    def formfield(self, **kwargs):
        kwargs.update({"widget": TypeaheadMarkdownWidget})
        return super().formfield(**kwargs)
