# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from urllib.parse import urlparse

from django import template
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.safestring import mark_safe

register = template.Library()


_url_validator = URLValidator()


@register.filter
def domain(url: str) -> str:
    try:
        _url_validator(url)
    except ValidationError:
        return url
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return mark_safe(f'<a href="{url}" rel="nofollow">{domain}</a>')
