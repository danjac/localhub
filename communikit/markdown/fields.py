from typing import Set, Optional

from django.db.models import Model, Field
from django.utils.encoding import mark_safe

from markdownx.models import MarkdownxField

from communikit.markdown.utils import markdownify, extract_mentions


class MarkdownProxy(str):
    def markdown(self) -> str:
        return mark_safe(markdownify(self))

    def extract_mentions(self) -> Set[str]:
        return extract_mentions(self)


class MarkdownFieldDescriptor(object):
    def __init__(self, field: Field):
        self.field = field

    def __get__(self, instance=None, owner=None) -> Optional[MarkdownProxy]:
        value = instance.__dict__[self.field]
        if value is None:
            return value
        return MarkdownProxy(value)

    def __set__(self, instance, value):
        instance.__dict__[self.field] = value


class MarkdownField(MarkdownxField):
    def contribute_to_class(self, cls: Model, name: str):
        super(MarkdownField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, MarkdownFieldDescriptor(self.name))
