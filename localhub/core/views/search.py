# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.functional import cached_property


class SearchMixin:
    search_query_parameter = "q"

    @cached_property
    def search_query(self) -> str:
        return self.request.GET.get(self.search_query_parameter, "")
