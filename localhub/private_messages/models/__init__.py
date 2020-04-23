# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone

from model_utils.models import TimeStampedModel

from localhub.bookmarks.models import Bookmark
from localhub.communities.models import Community
from localhub.db.generic import get_generic_related_queryset
from localhub.db.search import SearchIndexer
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification

from .querysets import MessageQuerySet


class Message(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_messages",
        on_delete=models.CASCADE,
    )

    message = MarkdownField()

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

    bookmarks = GenericRelation(Bookmark, related_query_name="message")

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
        """Returns absolute URL including complete community URL.

        Returns:
            str
        """
        return self.community.resolve_url(self.get_absolute_url())

    def get_notifications(self):
        return get_generic_related_queryset(self, Notification)

    def abbreviate(self, length=30):
        """Returns *final* non-HTML/markdown abbreviated version of message.

        Args:
            length (int, optional): abbreviated max length (default: 30)

        Returns:
            str
        """
        text = " ".join(self.message.plaintext().splitlines())
        total_length = len(text)
        if total_length < length:
            return text
        return "..." + text[total_length - length :]

    def accessible_to(self, user):
        """
        Checks if user is a) sender or recipient and b) has not deleted
        the message.

        Args:
            user (User): sender or recipient

        Returns:
            bool
        """
        return (self.sender == user and self.sender_deleted is None) or (
            self.recipient == user and self.recipient_deleted is None
        )

    def soft_delete(self, user):
        """Does a "soft delete":

        If user is recipient, sets recipient_deleted to current time.
        If user is sender, sets sender_deleted to current time.
        If both are set then the message itself is permanently deleted.

        Args:
            user (User): sender or recipient
        """
        field = "recipient_deleted" if user == self.recipient else "sender_deleted"
        setattr(self, field, timezone.now())
        if self.recipient_deleted and self.sender_deleted:
            self.delete()
        else:
            self.save(update_fields=[field])

    def get_parent(self, user):
        """Returns parent if exists and is visible to user.

        Args:
            user (User): sender or recipient
        Returns:
            Message or None
        """

        if self.parent and self.parent.accessible_to(user):
            return self.parent
        return None

    def get_other_user(self, user):
        """Return either recipient or sender, depending on user match,
        i.e. if user is the sender, returns the recipient, and vice
        versa.

        Args:
            user (User): sender or recipient

        Returns:
            User: recipient or sender
        """
        return self.recipient if user == self.sender else self.sender

    def mark_read(self, mark_replies=False):
        """Marks message read. Any associated Notification instances
        are marked read. Any unread messages or messages where user is
        not the recipient are ignored.

        Args:
            mark_replies (bool, optional): mark all replies read if recipient (default: False)
        """

        if not self.read:
            self.read = timezone.now()
            self.save(update_fields=["read"])
            self.get_notifications().mark_read()

            if mark_replies:
                self.get_all_replies().for_recipient(self.recipient).mark_read()

    def get_all_replies(self):
        """
        Returns:
            QuerySet: all replies including replies' descendants (recursive).
        """

        return self.__class__._default_manager.all_replies(self)

    def make_notification(self, verb):
        return Notification(
            content_object=self,
            actor=self.sender,
            recipient=self.recipient,
            community=self.community,
            verb=verb,
        )

    @dispatch
    def notify_on_send(self):
        """Send notification to recipient.

        Returns:
            Notification
        """
        return self.make_notification("send")

    @dispatch
    def notify_on_reply(self):
        """Send notification to recipient.

        Returns:
            Notification
        """
        return self.make_notification("reply")

    @dispatch
    def notify_on_follow_up(self):
        """Send notification to recipient.

        Returns:
            Notification
        """
        return self.make_notification("follow_up")
