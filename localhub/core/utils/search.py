# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce


from django.contrib.postgres.search import (
    SearchVector,
    SearchRank,
    SearchQuery,
)
from django.db import models


class SearchQuerySetMixin:
    search_document_field = "search_document"

    def search(self, search_term, search_rank_annotated_name="rank"):
        """
        Returns result of search on indexed fields. Annotates with
        `rank` to allow ordering by search result accuracy.
        """
        if not search_term:
            return self.none()
        query = SearchQuery(search_term)
        return self.annotate(
            **{
                search_rank_annotated_name: SearchRank(
                    models.F(self.search_document_field), query=query
                )
            }
        ).filter(**{self.search_document_field: query})


class InstanceSearchIndexer:
    def __init__(
        self, instance, owner, search_components, search_document_field
    ):
        self.instance = instance
        self.owner = owner
        self.search_components = search_components
        self.search_document_field = search_document_field

    def get_search_vectors(self):
        return [
            SearchVector(
                models.Value(text, output_field=models.CharField()),
                weight=weight,
            )
            for (weight, text) in [
                (k, getattr(self.instance, v))
                for k, v in self.search_components
            ]
        ]

    def update(self):
        """
        In e.g.post_save signal:

        transaction.on_commit(lambda: instance.search_indexer.update())
        """

        self.owner.objects.filter(pk=self.instance.pk).update(
            **{
                self.search_document_field: reduce(
                    operator.add, self.get_search_vectors()
                )
            }
        )


class SearchIndexer:
    """
    Example:

    class Post(Activity):

        ...
        search_document = SearchVectorField(null=True, editable=False)

        search_indexer = SearchIndexer((
            ("A", "title"),
            ("B", "description")
        ))
    """

    def __init__(
        self, *search_components, search_document_field="search_document"
    ):
        self.search_components = search_components
        self.search_document_field = search_document_field

    def __get__(self, instance, owner):
        return InstanceSearchIndexer(
            instance,
            owner,
            self.search_components,
            search_document_field=self.search_document_field,
        )
