# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.db import models


class NotificationQuerySet(models.QuerySet):
    def for_community(self, community):
        """Filter notifications for a community, including
        only those with actors who are active members.

        Args:
            community (Community)

        Returns:
            QuerySet
        """

        return self.filter(
            community=community,
            actor__membership__community=community,
            actor__membership__active=True,
            actor__is_active=True,
        )

    def exclude_blocked_actors(self, recipient):
        """Exclude all notifications with actors blocked by the recipient.

        Args:
            recipient (User): notification recipient

        Returns:
            QuerySet
        """

        return self.exclude(actor__in=recipient.blocked.all())

    def for_recipient(self, recipient):
        """Return all notifications for a recipient

        Args:
            recipient (User): notification recipient

        Returns:
            QuerySet
        """

        return self.filter(recipient=recipient)

    def unread(self):
        """Return all notifications with is_read=False

        Returns:
            QuerySet
        """

        return self.filter(is_read=False)

    def mark_read(self):
        """Marks all notifications read if they are unread.

        Returns:
            int -- number updated
        """

        return self.unread().update(is_read=True)


class NotificationManager(models.Manager.from_queryset(NotificationQuerySet)):

    ...
