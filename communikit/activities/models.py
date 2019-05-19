import operator

from functools import reduce
from typing import Callable

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchVector,
    SearchVectorField,
    SearchRank,
    SearchQuery,
)
from django.db import models

from model_utils.managers import InheritanceQuerySetMixin
from model_utils.models import TimeStampedModel


from communikit.communities.models import Community


class ActivityQuerySet(InheritanceQuerySetMixin, models.QuerySet):
    def with_num_comments(self) -> models.QuerySet:
        return self.annotate(num_comments=models.Count("comment"))

    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("like"))

    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        if user.is_authenticated:
            return self.annotate(
                has_liked=models.Exists(
                    user.like_set.filter(activity=models.OuterRef("pk"))
                )
            )
        return self.annotate(
            has_liked=models.Value(False, output_field=models.BooleanField())
        )

    def search(self, search_term: str) -> models.QuerySet:
        query = SearchQuery(search_term)
        return self.annotate(
            rank=SearchRank(models.F("search_document"), query=query)
        ).filter(search_document=query)


class Activity(TimeStampedModel):
    """
    Base class for all activity-related entities e.g. posts, events, photos.
    """

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    search_document = SearchVectorField(null=True)

    objects = ActivityQuerySet.as_manager()

    class Meta:
        indexes = [GinIndex(fields=["search_document"])]

    def get_absolute_url(self) -> str:
        # TBD: we should have a "routing" URL for activities that finds
        # the correct subclass and redirects there.
        return "/"

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    # set up signal for each subclass
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


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "activity")
