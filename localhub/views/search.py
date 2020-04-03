# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.functional import cached_property


class SearchMixin:
    search_query_parameter = "q"
    search_optional = True

    @cached_property
    def search_query(self):
        return self.request.GET.get(self.search_query_parameter, "")

    def get_context_data(self, **kwargs):
        """
        Add query string wihout search query parameter
        """
        data = super().get_context_data(**kwargs)
        non_search_params = self.request.GET.copy()
        for param in ("page", self.search_query_parameter):
            if param in non_search_params:
                del non_search_params[param]
        non_search_path = self.request.path
        if non_search_params:
            non_search_path += "?" + non_search_params.urlencode()
        data.update(
            {
                "non_search_params": non_search_params,
                "non_search_path": non_search_path,
            }
        )
        return data
