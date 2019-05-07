from django import template
from django.conf import settings
from django.db import models

from communikit.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def has_liked(
    context: ContextDict, user: settings.AUTH_USER_MODEL, obj: models.Model
) -> bool:
    return context["request"].has_liked(obj)
