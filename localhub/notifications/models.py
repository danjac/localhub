# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel
from pywebpush import WebPushException, webpush

from localhub.communities.models import Community


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


class Notification(TimeStampedModel):
    """
    If you define a model as a content_object of this class, you must register
    the model with a Adapter subclass in a notifications module
    under the model app.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    verb = models.CharField(max_length=30)
    is_read = models.BooleanField(default=False)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "created", "-created", "is_read",]
            )
        ]


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    endpoint = models.TextField()
    auth = models.TextField()
    p256dh = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "auth", "p256dh", "community"],
                name="unique_push_notification",
            )
        ]

    def push(self, payload, ttl=0):
        """Sends push notification.
        If sub has expired, will delete the instance.

        This should probably be called asynchronously e.g. in celery.

        Args:
            payload (dict): webpush payload e.g. "header", "body", "url"
            ttl (int, optional): time to live (default: 0)

        Returns:
            bool: if webpush succeeds

        Raises:
            WebPushException
        """

        subscription_info = {
            "endpoint": self.endpoint,
            "keys": {"auth": self.auth, "p256dh": self.p256dh},
        }

        vapid_creds = {}
        if settings.VAPID_PRIVATE_KEY:
            vapid_creds["vapid_private_key"] = settings.VAPID_PRIVATE_KEY
        if settings.VAPID_ADMIN_EMAIL:
            vapid_creds["vapid_claims"] = {
                "sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"
            }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                ttl=ttl,
                **vapid_creds,
            )
            return True
        except WebPushException as e:
            if e.response.status_code == 410:  # timeout
                self.delete()
            else:
                raise e

        return False
