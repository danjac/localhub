from django import template
from django.db import models

from communikit.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def has_liked(context: ContextDict, obj: models.Model) -> bool:
    # TBD: we're getting rid of this and using model annotations
    return context["request"].has_liked(obj)
