# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
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

    def with_num_replies(self, user):
        return self.annotate(
            num_replies=models.Count(
                "replies",
                filter=models.Q(
                    models.Q(
                        replies__recipient=user,
                        replies__recipient_deleted__isnull=True,
                    )
                    | models.Q(
                        replies__sender=user, replies__sender_deleted__isnull=True,
                    )
                ),
                distinct=True,
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
        related_name="children",
    )

    # immediate parent
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
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

    def resolve_url(self, user=None, is_thread=False):
        """
        Resolves the correct URL for this message:

        1) if is_thread then just returns the hash.
        2) if has a *visible* thread returns the thread absolute URL + hash.
        3) if no thread then returns the absolute URL of this message.
        """
        hash = f"#message-{self.id}"
        if is_thread:
            return hash
        if user and (thread := self.get_thread(user)):
            return f"{thread.get_absolute_url()}{hash}"
        return self.get_absolute_url()

    def get_permalink(self, user=None):
        return self.community.resolve_url(self.resolve_url(user))

    def abbreviate(self, length=30):
        """
        Returns *final* non-HTML/markdown abbreviated version of message.
        """
        text = " ".join(self.message.plaintext().splitlines())
        total_length = len(text)
        if total_length < length:
            return text
        return "..." + text[total_length - length :]

    def is_visible(self, user):
        """
        Checks if user is a) sender or recipient and b) has not deleted
        the message.
        """
        return (self.sender == user and self.sender_deleted is None) or (
            self.recipient == user and self.recipient_deleted is None
        )

    def get_thread(self, user):
        """
        Returns thread if exists and is visible to user, otherwise returns None.
        """
        if self.thread and self.thread.is_visible(user):
            return self.thread
        return None

    def get_parent(self, user):
        """
        Returns parent if exists and is visible to user, otherwise returns None.
        """
        if self.parent and self.parent.is_visible(user):
            return self.parent
        return None

    def get_other_user(self, user):
        """
        Return either recipient or sender, depending on user match
        """
        return self.recipient if user == self.sender else self.sender

    def mark_read(self):
        if not self.read:
            self.read = timezone.now()
            self.save(update_fields=["read"])
