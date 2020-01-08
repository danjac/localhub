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
        return self.filter(
            community=community,
            actor__membership__community=community,
            actor__membership__active=True,
            actor__is_active=True,
        )


class Notification(TimeStampedModel):
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
        """
        Sends push notification.
        If sub has expired, will delete the instance.
        Returns True if sent.

        This should probably be called in a celery task.
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
