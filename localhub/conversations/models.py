# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.utils.search import SearchIndexer, SearchQuerySetMixin


class MessageQuerySet(SearchQuerySetMixin, models.QuerySet):
    ...


class Message(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    message = MarkdownField()

    read = models.DateTimeField(null=True, blank=True)

    search_document = SearchVectorField(null=True, editable=False)
    search_indexer = SearchIndexer(("A", "message"))

    objects = MessageQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["created", "-created", "read"]),
        ]

    def __str__(self) -> str:
        return self.message

    def get_absolute_url(self) -> str:
        return reverse("conversations:message_detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())
