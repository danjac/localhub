# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import functools

# Django
from django.utils.functional import SimpleLazyObject


class Search:
    search_parameter = "q"

    def __init__(self, request):
        self.request = request

    @functools.lru_cache
    def __str__(self):
        return self.request.GET.get(self.search_parameter, "").strip()

    def __bool__(self):
        return bool(str(self))


class SearchMiddleware:
    """
    Checks for search parameter, added as `request.search`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.search = SimpleLazyObject(lambda: Search(request))
        return self.get_response(request)
