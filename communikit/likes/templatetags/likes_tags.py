from django import template
from django.conf import settings
from django.db import models

from communikit.likes.models import Like

register = template.Library()


@register.simple_tag
def has_liked(user: settings.AUTH_USER_MODEL, obj: models.Model) -> bool:
    return Like.objects.user_has_liked(user, obj)
