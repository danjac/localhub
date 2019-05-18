from django import template
from django.db.models import Model

register = template.Library()


@register.filter
def model_name(instance: Model) -> str:
    return instance._meta.model_name
