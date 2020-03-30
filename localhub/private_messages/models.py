# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from model_utils.models import TimeStampedModel

from localhub.bookmarks.models import Bookmark, BookmarkAnnotationsQuerySetMixin
from localhub.communities.models import Community
from localhub.db.content_types import (
    get_generic_related_queryset,
    get_multiple_generic_related_queryset,
)
from localhub.db.search import SearchIndexer, SearchQuerySetMixin
from localhub.markdown.fields import MarkdownField
from localhub.notifications.decorators import dispatch
from localhub.notifications.models import Notification


class MessageQuerySet(
    SearchQuerySetMixin, BookmarkAnnotationsQuerySetMixin, models.QuerySet
):
    def for_community(self, community):
        """Returns messages available to this community, where both
        sender and recipient are active members.

        Args:
            community (Community)

        Returns:
            QuerySet
        """
        return self.filter(
            community=community,
            sender__membership__community=community,
            sender__membership__active=True,
            sender__is_active=True,
            recipient__membership__community=community,
            recipient__membership__active=True,
            recipient__is_active=True,
        )

    def for_sender(self, sender):
        """Returns messages sent by this user. Does not
        include any deleted by this user.

        Args:
            sender (User)

        Returns:
            QuerySet
        """
        return self.filter(sender=sender, sender_deleted__isnull=True)

    def for_recipient(self, recipient):
        """Returns messages received by this user. Does not
        include any deleted by this user.

        Args:
            recipient (User)

        Returns:
            QuerySet
        """
        return self.filter(recipient=recipient, recipient_deleted__isnull=True)

    def for_sender_or_recipient(self, user):
        """Returns messages either sent or received by this user.

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return self.for_sender(user) | self.for_recipient(user)

    def from_sender_to_recipient(self, sender, recipient):
        """Returns messages from specific sender and recipient

        Args:
            sender (User)
            recipient (User)

        Returns:
            QuerySet
        """

        return self.for_sender(sender).for_recipient(recipient)

    def between(self, current_user, other_user):
        """Return all messages exchanged between two users.

        Args:
            current_user (User)
            other_user (User)

        Returns:
            QuerySet
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
        """Exclude:
        1) user is blocked by sender
        2) user is blocking sender

        Args:
            user (User): recipient

        Returns:
            QuerySet
         """
        return self.exclude(
            models.Q(sender__blockers=user) | models.Q(sender__blocked=user)
        )

    def exclude_recipient_blocked(self, user):
        """Exclude:
        1) user is blocked by recipient
        2) user is blocking recipient

        Args:
            user (User): recipient

        Returns:
            QuerySet
         """
        return self.exclude(
            models.Q(recipient__blockers=user) | models.Q(recipient__blocked=user)
        )

    def exclude_blocked(self, user):
        """Exclude if:
        1) user is blocked by recipient
        2) user is blocking recipient
        3) user is blocked by sender
        4) user is blocking sender

        Args:
            user (User): sender or recipient

        Returns:
            QuerySet
        """
        return self.exclude_sender_blocked(user).exclude_recipient_blocked(user)

    def unread(self):
        return self.filter(read__isnull=True)

    def reply_count_subquery(self, replies):
        return models.Subquery(
            replies.values("parent").annotate(count=models.Count("pk")).values("count"),
            output_field=models.IntegerField(),
        )

    def with_num_replies(self, user):
        """
        Annotated queryset with num_replies (replies to own messages).

        Args:
            user (User): recipient/sender

        Returns:
            QuerySet
        """
        return self.annotate(
            num_replies=self.reply_count_subquery(
                self.model._default_manager.for_sender_or_recipient(user)
                .filter(parent=models.OuterRef("pk"))
                .exclude(sender=models.OuterRef("sender"))
            )
        )

    def with_num_follow_ups(self, user):
        """
        Annotated queryset with num_follow_ups (replies to own messages).

        Args:
            user (User): recipient/sender

        Returns:
            QuerySet
        """
        return self.annotate(
            num_follow_ups=self.reply_count_subquery(
                self.model._default_manager.for_sender_or_recipient(user).filter(
                    parent=models.OuterRef("pk"), sender=models.OuterRef("sender")
                )
            )
        )

    def with_common_annotations(self, user):
        """Wraps  `with_num_follow_ups` and `with_num_replies`.

        Args:
            user (User): recipient/sender

        Returns:
            QuerySet
        """
        return self.with_num_follow_ups(user).with_num_replies(user)

    def mark_read(self):
        """Mark read any un-read items

        Returns:
            int: number of messages updated
        """
        self.notifications().unread().mark_read()
        return self.unread().update(read=timezone.now())

    def notifications(self):
        """
        Returns:
            QuerySet: Notifications associated with objects in this QuerySet
        """
        return get_multiple_generic_related_queryset(self, Notification)


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

    def is_visible(self, user):
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

    def get_thread(self, user):
        """Returns thread (grandfather message)
        if exists and is visible to user.

        Args:
            user (User): sender or recipient
        Returns:
            Message or None
        """

        if self.thread and self.thread.is_visible(user):
            return self.thread
        return None

    def get_parent(self, user):
        """Returns parent if exists and is visible to user.

        Args:
            user (User): sender or recipient
        Returns:
            Message or None
        """

        if self.parent and self.parent.is_visible(user):
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

    def mark_read(self):
        """Marks message read. Any associated Notification instances
        are marked read.
        """
        if not self.read:
            self.read = timezone.now()
            self.save(update_fields=["read"])
            self.get_notifications().unread().mark_read()

    @dispatch
    def notify(self):
        """Send notification to recipient.

        Returns:
            Notification
        """
        return Notification(
            content_object=self,
            actor=self.sender,
            recipient=self.recipient,
            community=self.community,
            verb="message",
        )
