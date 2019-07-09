# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template

from communikit.core.types import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(context: ContextDict, page_number: int) -> str:
    request = context["request"]
    params = request.GET.copy()
    params["page"] = page_number
    return request.path + "?" + params.urlencode()
