# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Iterable, List

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from model_utils.models import TimeStampedModel

from localhub.communities.models import Community
from localhub.core.types import BaseQuerySetMixin
from localhub.core.utils.content_types import get_generic_related_exists
from localhub.notifications.models import Notification


class SubscriptionAnnotationsQuerySetMixin(BaseQuerySetMixin):
    """
    Adds annotation methods to related model query set.
    """

    def with_has_subscribed(
        self, user: settings.AUTH_USER_MODEL, community: Community
    ) -> models.QuerySet:
        """
        Adds `has_subscribed` Boolean value whether user has subscribed
        to each object.
        """
        return self.annotate(
            has_subscribed=get_generic_related_exists(
                self.model,
                Subscription.objects.filter(
                    subscriber=user, community=community
                ),
            )
        )


class Subscription(TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "content_type", "object_id"],
                name="unique_subscription",
            )
        ]
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "subscriber", "community"]
            )
        ]

    def notify(
        self, recipients: Iterable[settings.AUTH_USER_MODEL]
    ) -> List[Notification]:
        """
        Sends notification to provided recipients
        """

        notifications = [
            Notification(
                content_object=self.content_object,
                recipient=recipient,
                actor=self.subscriber,
                community=self.community,
                verb="subscribe",
            )
            for recipient in recipients
        ]

        Notification.objects.bulk_create(notifications)
        return notifications
