# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


"""
Custom functionality for the Markdownx field.

This provides additional methods on the field:

- obj.description.markdown() -> returns safe HTML string
- obj.description.extract_mentions() -> returns set of "@" mention strings
- obj.description.extract_hashtags() -> returns set of "#" tag strings
"""

from typing import Set, Optional, Type

from django.db.models import Model, Field
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from .utils import markdownify, extract_mentions, extract_hashtags


class MarkdownProxy(str):
    def markdown(self) -> str:
        return mark_safe(markdownify(self))

    def extract_mentions(self) -> Set[str]:
        return extract_mentions(self)

    def extract_hashtags(self) -> Set[str]:
        return extract_hashtags(self)


class MarkdownFieldDescriptor:
    def __init__(self, field: Field):
        self.field = field

    def __get__(
        self,
        instance: Optional[Model] = None,
        owner: Optional[Type[Model]] = None,
    ) -> Optional[MarkdownProxy]:
        value = instance.__dict__[self.field]
        if value is None:
            return value
        return MarkdownProxy(value)

    def __set__(self, instance: Model, value: Optional[str]):
        instance.__dict__[self.field] = value


class MarkdownField(MarkdownxField):
    def contribute_to_class(self, cls: Model, name: str):
        super(MarkdownField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, MarkdownFieldDescriptor(self.name))
