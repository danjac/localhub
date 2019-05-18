import operator

from collections import defaultdict
from functools import reduce
from typing import Callable, Dict

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.core.paginator import Page, Paginator
from django.db import models

from model_utils.models import TimeStampedModel


from communikit.communities.models import Community


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    # all activities belong to a single community (at this point)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    # all activities are created by someone (this will become "owner" later)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    search_document = SearchVectorField(null=True)

    class Meta:
        abstract = True
        indexes = [GinIndex(fields=["search_document"])]

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    def make_search_updater(self) -> Callable:
        def on_commit():
            search_vectors = [
                SearchVector(models.Value(text), weight=weight)
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_document=reduce(operator.add, search_vectors)
            )

        return on_commit


def activity_stream(
    queryset_dict: Dict[str, models.QuerySet],
    order_by: str = "created",
    **paginator_kwargs,
) -> Page:
    """
    Returns a paginated activity stream using a union of
    different querysets of Activity subclasses.

    Inspired by
    https://simonwillison.net/2018/Mar/25/combined-recent-additions/
    Usage:

    page = activity_stream({
        "post": Post.objects.all(),
        "event": Event.objects.all(),
    }, page_number=1)
    """
    querysets = [
        queryset.annotate(
            activity_type=models.Value(key, output_field=models.CharField())
        ).values("pk", "activity_type", order_by)
        for key, queryset in queryset_dict.items()
    ]
    union_qs = querysets[0].union(*querysets[1:]).order_by(f"-{order_by}")
    page_number = paginator_kwargs.pop("page_number", 1)
    page = Paginator(union_qs, **paginator_kwargs).get_page(page_number)
    # bulk load each object type
    to_load = defaultdict(set)
    for result in page:
        to_load[result["activity_type"]].add(result["pk"])
    fetched = {}
    for key, pks in to_load.items():
        for item in queryset_dict[key].filter(pk__in=pks):
            fetched[(key, item.pk)] = item
    # annotate results with object
    for result in page:
        result["object"] = fetched[(result["activity_type"], result["pk"])]
    return page


def activity_search(
    search_term: str,
    queryset_dict: Dict[str, models.QuerySet],
    **paginator_kwargs,
) -> Page:
    """
    Works like activity_stream but returns result of query across all
    querysets.
    """
    query = SearchQuery(search_term)
    rank = SearchRank(models.F("search_document"), query)

    queryset_dicts = {
        key: qs.annotate(rank=rank).filter(search_vector=query)
        for key, qs in queryset_dict.items()
    }
    return activity_stream(queryset_dicts, order_by="rank", **paginator_kwargs)
