# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils import timezone
from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.db.search import SearchIndexer, SearchQuerySetMixin
from localhub.markdown.fields import MarkdownField


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
        return self.filter(sender=user, sender_deleted__isnull=True)

    def for_recipient(self, user):
        return self.filter(recipient=user, recipient_deleted__isnull=True)

    def for_sender_or_recipient(self, user):
        return self.for_sender(user) | self.for_recipient(user)

    def between(self, current_user, other_user):
        """
        Return all messages exchanged between two users.
        """
        return self.filter(
            models.Q(
                models.Q(
                    sender=current_user,
                    sender_deleted__isnull=True,
                    recipient=other_user,
                )
                | models.Q(
                    recipient=current_user,
                    recipient_deleted__isnull=True,
                    sender=other_user,
                )
            )
        ).distinct()

    def exclude_sender_blocked(self, user):
        """
        Exclude:
        1) user is blocked by sender
        2) user is blocking sender
        """
        return self.exclude(
            models.Q(sender__blockers=user) | models.Q(sender__blocked=user)
        )

    def exclude_recipient_blocked(self, user):
        """
        Exclude:
        1) user is blocked by recipient
        2) user is blocking recipient
        """
        return self.exclude(
            models.Q(recipient__blockers=user) | models.Q(recipient__blocked=user)
        )

    def exclude_blocked(self, user):
        """
        Exclude:
        1) user is blocked by recipient
        2) user is blocking recipient
        3) user is blocked by sender
        4) user is blocking sender
        """
        return self.exclude_sender_blocked(user).exclude_recipient_blocked(user)

    def unread(self):
        return self.filter(read__isnull=True)

    def with_has_thread(self, user):
        return self.annotate(
            has_thread=models.Exists(
                Message.objects.for_sender_or_recipient(user).filter(
                    thread=models.OuterRef("pk")
                )
            )
        )

    def mark_read(self):
        """
        Mark read any un-read items
        """
        return self.unread().update(read=timezone.now())


class Message(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    message = MarkdownField()

    thread = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )

    # immediate parent
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    read = models.DateTimeField(null=True, blank=True)

    recipient_deleted = models.DateTimeField(null=True, blank=True)
    sender_deleted = models.DateTimeField(null=True, blank=True)

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

    def get_absolute_url(self):
        return reverse("private_messages:message_detail", args=[self.id])

    def get_permalink(self):
        return self.community.resolve_url(self.get_absolute_url())

    def abbreviate(self, length=30):
        """
        Returns non-HTML/markdown abbreviated version of message.
        """
        text = " ".join(self.message.plaintext().splitlines())
        return truncatechars(text, length)

    def is_visible(self, user):
        """
        Checks if user is a) sender or recipient and b) has not deleted
        the message.
        """
        return (self.sender == user and self.sender_deleted is None) or (
            self.recipient == user and self.recipient_deleted is None
        )

    def get_other_user(self, user):
        """
        Return either recipient or sender, depending on user match
        """
        return self.recipient if user == self.sender else self.sender

    def mark_read(self):
        if not self.read:
            self.read = timezone.now()
            self.save(update_fields=["read"])
