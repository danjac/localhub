# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils import timezone

from localhub.bookmarks.models.mixins import BookmarkAnnotationsQuerySetMixin
from localhub.db.generic import get_generic_related_queryset
from localhub.db.search import SearchQuerySetMixin
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

    def common_select_related(self):
        """
        Joins related models for most common operations on views:

            - sender
            - recipient
            - community
            - parent + sender/recipient

        Returns:
            QuerySet
        """
        return self.select_related(
            "sender",
            "recipient",
            "community",
            "parent",
            "parent__sender",
            "parent__recipient",
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

    def with_num_replies(self, user):
        """
        Annotated queryset with num_replies (replies to own messages).

        Args:
            user (User): recipient/sender

        Returns:
            QuerySet
        """
        return self.annotate(
            num_replies=self._reply_count_subquery(
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
            num_follow_ups=self._reply_count_subquery(
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

    def all_replies(self, parent):
        """
        Does a recursive query, returning all descendants of this message (
            direct replies + all their replies.
        )

        Args:
            parent (Message): top-level message parent/grandparent

        Returns:
            QuerySet
        """

        # does PostgreSQL WITH RECURSIVE

        table_name = self.model._meta.db_table

        query = (
            "WITH RECURSIVE children (id) AS ("
            f"SELECT {table_name}.id FROM {table_name} WHERE id={parent.pk} "
            f"UNION ALL SELECT {table_name}.id FROM children, {table_name} "
            f"WHERE {table_name}.parent_id=children.id)"
            f"SELECT {table_name}.id FROM {table_name}, children "
            f"WHERE children.id={table_name}.id AND {table_name}.id != {parent.pk}"
        )

        return self.filter(pk__in=[obj.id for obj in self.raw(query)])

    def mark_read(self):
        """Mark read any un-read items. Associated Notifications
        are also marked read.

        Args:
            recipient (User): recipient reading the messages

        Returns:
            int: number of messages updated
        """
        q = self.unread()
        q.notifications().mark_read()
        return q.update(read=timezone.now())

    def notifications(self):
        """
        Returns:
            QuerySet: Notifications associated with objects in this QuerySet
        """
        return get_generic_related_queryset(self, Notification)

    def _reply_count_subquery(self, replies):
        return models.Subquery(
            replies.values("parent").annotate(count=models.Count("pk")).values("count"),
            output_field=models.IntegerField(),
        )
