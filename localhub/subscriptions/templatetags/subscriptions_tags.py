# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from localhub.subscriptions.models import Subscription

register = template.Library()


@register.simple_tag
def is_subscribed(user: settings.AUTH_USER_MODEL, obj: Model) -> bool:

    if user.is_anonymous:
        return False

    return Subscription.objects.filter(
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
        subscriber=user,
    ).exists()
