# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    Base abstract model. For every model we want to add notifications:

    1) create a subclass e.g. PostNotification
    2) add appropriate signals (post_save etc)
    3) add a MarkRead view :
        path(
            'notifications/mark-read/<int:pk>/',
            NotificationMarkReadView.as_view(model=PostNotification),
            name="mark-read"
        )

    def match_usernames(self, names: Sequence[str]) -> QuerySet:
        return self.filter(username__regex=r'^(%s) +' % '|'.join(names))

    def notify(self, created: bool) -> List["PostNotification"]:
        notifications = []
        if self.description_tracker.changed:
            notifications += [
                PostNotification(
                    post=self,
                    recipient=recipient,
                    verb="mentioned",
                ) for recipient in self.community.members.match_usernames(
                    self.description.extract_mentions()
                )
            ]
        verb = "created" if created else "updated"
        notifications += [
            PostNotification(
                post=self,
                community=self.community,
                recipient=recipient,
                verb=verb,
            ) for recipient in self.community.get_moderators()
        ]
        PostNotification.objects.bulk_create(notifications)
        return notifications
        """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    verb = models.CharField(max_length=20)
    is_read = models.BooleanField(default=False)

    class Meta:
        abstract = True
