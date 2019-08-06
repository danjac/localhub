# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urlparse

from django import template
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.safestring import mark_safe

from localhub.activities.models import Activity

register = template.Library()


_url_validator = URLValidator()


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
    try:
        _url_validator(url)
    except ValidationError:
        return url
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return mark_safe(f'<a href="{url}" rel="nofollow">{domain}</a>')
