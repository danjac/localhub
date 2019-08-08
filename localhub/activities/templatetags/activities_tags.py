# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from localhub.activities.models import Activity
from localhub.activities.utils import get_domain

register = template.Library()


@register.filter
def is_content_sensitive(
    activity: Activity, user: settings.AUTH_USER_MODEL
) -> bool:
    if user.is_authenticated and user.show_sensitive_content:
        return False
    return bool(activity.get_content_warning_tags())


@register.filter
def oembed_fallback(url: str) -> str:
    """
    Show instead of oembed content, if unavailable or blocked.
    """
    domain = get_domain(url)
    if domain:
        return mark_safe(f'<a href="{url}" rel="nofollow">{domain}</a>')
    return url
