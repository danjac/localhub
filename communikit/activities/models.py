# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce
from typing import Callable, Optional

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    SearchVectorField,
)
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import gettext as _

from model_utils.managers import InheritanceQuerySetMixin
from model_utils.models import TimeStampedModel


from communikit.communities.models import Community
from communikit.core.types import BreadcrumbList


class ActivityQuerySet(InheritanceQuerySetMixin, models.QuerySet):
    """
    Note: InheritanceQuerySet is buggy, it doesn't handle
    multple annotations:
    https://github.com/jazzband/django-model-utils/issues/312
    so we'll use it only when absolutely necessary.
    """

    def with_num_comments(self) -> models.QuerySet:
        return self.annotate(
            num_comments=models.Count("comment", distinct=True)
        )

    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("like", distinct=True))

    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        if user.is_authenticated:
            return self.annotate(
                has_liked=models.Exists(
                    Like.objects.filter(
                        user=user, activity=models.OuterRef("pk")
                    )
                )
            )
        return self.annotate(
            has_liked=models.Value(False, output_field=models.BooleanField())
        )

    def search(self, search_term: str) -> models.QuerySet:
        if not search_term:
            return self.none()
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

    search_document = SearchVectorField(null=True, editable=False)

    objects = ActivityQuerySet.as_manager()

    list_url_name: Optional[str] = None
    detail_url_name: Optional[str] = None

    class Meta:
        indexes = [GinIndex(fields=["search_document"])]

    def slugify(self) -> str:
        return slugify(smart_text(self), allow_unicode=False)

    def get_absolute_url(self) -> str:
        return reverse(self.detail_url_name, args=[self.id, self.slugify()])

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())

    def get_breadcrumbs(self) -> BreadcrumbList:
        return [
            (reverse("activities:stream"), _("Home")),
            (
                reverse(self.list_url_name),
                _(self._meta.verbose_name_plural.title()),
            ),
            (self.get_absolute_url(), truncatechars(smart_text(self), 60)),
        ]

    # https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/
    def search_index_components(self):
        return {}

    # in post_save: transaction.on_commit(instance.make_search_updater())
    # set up signal for each subclass
    def make_search_updater(self) -> Callable:
        def on_commit():
            search_vectors = [
                SearchVector(
                    models.Value(text, output_field=models.CharField()),
                    weight=weight,
                )
                for (weight, text) in self.search_index_components().items()
            ]
            self.__class__.objects.filter(pk=self.pk).update(
                search_document=reduce(operator.add, search_vectors)
            )

        return on_commit


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "activity")
