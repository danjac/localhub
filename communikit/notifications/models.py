# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel

from communikit.communities.models import Community


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

        notify function:
        notification = PostNotification.objects.create(
            post=post,
            community=post.community,
            recipient=mentioned,
            verb="mention",
        )
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    verb = models.CharField(max_length=20)
    is_read = models.BooleanField(default=False)

    class Meta:
        abstract = True
