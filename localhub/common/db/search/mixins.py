# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db import models
from django.utils.encoding import force_str


class SearchQuerySetMixin:
    search_document_field = "search_document"

    def search(self, search_term, search_rank_annotated_name="rank"):
        """
        Returns result of search on indexed fields. Annotates with
        `rank` to allow ordering by search result accuracy.
        """
        if not search_term:
            return self.none()
        query = SearchQuery(force_str(search_term), search_type="websearch")
        return self.annotate(
            **{
                search_rank_annotated_name: SearchRank(
                    models.F(self.search_document_field), query=query
                )
            }
        ).filter(**{self.search_document_field: query})
