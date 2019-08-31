# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template.defaultfilters import truncatechars, striptags
from django.urls import reverse

from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.core.markdown.fields import MarkdownField
from localhub.core.utils.search import SearchIndexer, SearchQuerySetMixin


class MessageQuerySet(SearchQuerySetMixin, models.QuerySet):
    def for_community(self, community):
        return self.filter(
            community=community,
            sender__membership__community=community,
            sender__membership__active=True,
            sender__is_active=True,
            recipient__membership__community=community,
            recipient__membership__active=True,
            recipient__is_active=True,
        )

    def for_sender(self, user):
        return self.filter(sender=user)

    def for_recipient(self, user):
        return self.filter(recipient=user)

    def for_sender_or_recipient(self, user):
        return self.filter(models.Q(sender=user) | models.Q(recipient=user))

    def between(self, user_a, user_b):
        """
        Return all messages exchanged between two users.
        """
        return self.filter(
            models.Q(recipient=user_a, sender=user_b)
            | models.Q(recipient=user_b, sender=user_a)
        )

    def with_sender_has_blocked(self, user):
        return self.annotate(
            sender_has_blocked=models.Exists(
                user.blockers.filter(pk=models.OuterRef("sender_id"))
            )
        )


class Message(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    message = MarkdownField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    read = models.DateTimeField(null=True, blank=True)

    search_document = SearchVectorField(null=True, editable=False)
    search_indexer = SearchIndexer(("A", "message"))

    objects = MessageQuerySet.as_manager()

    class Meta:
        indexes = [
            GinIndex(fields=["search_document"]),
            models.Index(fields=["created", "-created", "read"]),
        ]

    def __str__(self):
        return self.message

    def get_abbreviation(self, length=30):
        """
        Returns non-HTML/markdown abbreviated version of message.
        """
        text = " ".join(
            striptags(self.message.markdown()).strip().splitlines()
        )
        return truncatechars(text, length)

    def get_absolute_url(self):
        return reverse("private_messages:message_detail", args=[self.id])

    def get_permalink(self):
        return self.community.resolve_url(self.get_absolute_url())

    def get_other_user(self, user):
        """
        Return either recipient or sender, depending on user match
        """
        return self.recipient if user == self.sender else self.sender
