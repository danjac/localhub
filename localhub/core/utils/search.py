# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce

from typing import Callable, List, Tuple, Type

from django.contrib.postgres.search import (
    SearchVector,
    SearchRank,
    SearchQuery,
)
from django.db import models

from localhub.core.types import BaseQuerySetMixin
from localhub.core.utils.functional import nested_getattr


class SearchQuerySetMixin(BaseQuerySetMixin):
    search_document_field = "search_document"

    def search(
        self, search_term: str, search_rank_annotated_name: str = "rank"
    ) -> models.QuerySet:
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
        self,
        instance: models.Model,
        owner: Type[models.Model],
        search_components: Tuple[Tuple[str, str]],
        search_document_field: str,
    ):
        self.instance = instance
        self.owner = owner
        self.search_components = search_components
        self.search_document_field = search_document_field

    def get_search_vectors(self) -> List[SearchVector]:
        return [
            SearchVector(
                models.Value(text, output_field=models.CharField()),
                weight=weight,
            )
            for (weight, text) in [
                (k, nested_getattr(self.instance, v))
                for k, v in self.search_components
            ]
        ]

    def make_updater(self) -> Callable:
        """
        Returns an indexing function to update the PostgreSQL search document
        for this instance.

        In post_save signal:

        transaction.on_commit(instance.search_indexer.make_updater())
        """

        def on_commit():
            self.owner.objects.filter(pk=self.instance.pk).update(
                **{
                    self.search_document_field: reduce(
                        operator.add, self.get_search_vectors()
                    )
                }
            )

        return on_commit


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

    def __get__(
        self, instance: models.Model, owner: Type[models.Model]
    ) -> InstanceSearchIndexer:
        return InstanceSearchIndexer(
            instance,
            owner,
            self.search_components,
            search_document_field=self.search_document_field,
        )
