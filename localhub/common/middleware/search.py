# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import functools


class SearchMiddleware:
    """
    Checks for search parameter, added as `request.search`.
    """

    search_parameter = "q"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        @functools.lru_cache
        def _get_search():
            return request.GET.get(self.search_parameter, "").strip()

        request.search = _get_search()
        return self.get_response(request)
