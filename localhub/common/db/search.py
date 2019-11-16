# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools
import operator

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models, transaction


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

    def __init__(self, *search_components, search_document_field="search_document"):
        self.search_components = search_components
        self.search_document_field = search_document_field

    def get_search_vectors(self, instance):
        return [
            SearchVector(
                models.Value(text, output_field=models.CharField()), weight=weight,
            )
            for (weight, text) in [
                (k, getattr(instance, v)) for k, v in self.search_components
            ]
        ]

    def update_search_index(self, instance):
        self.cls.objects.filter(pk=instance.pk).update(
            **{
                self.search_document_field: functools.reduce(
                    operator.add, self.get_search_vectors(instance)
                )
            }
        )

    def finalize(self, sender, **kwargs):
        def update_search_document(instance, **kwargs):
            transaction.on_commit(lambda: self.update_search_index(instance))

        models.signals.post_save.connect(
            update_search_document, sender=sender, weak=False
        )

    def contribute_to_class(self, cls, name):

        self.cls = cls

        models.signals.class_prepared.connect(self.finalize, sender=cls, weak=False)
