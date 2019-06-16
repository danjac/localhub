# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List, Tuple

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _

from model_utils import FieldTracker

from communikit.activities.models import Activity
from communikit.core.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class Post(Activity):

    title = models.CharField(max_length=300, blank=True)
    description = MarkdownField(blank=True)
    url = models.URLField(blank=True)

    notifications = GenericRelation(Notification, related_query_name="post")

    description_tracker = FieldTracker(["description"])

    def __str__(self) -> str:
        return self.title or self.url or _("Post")

    def get_absolute_url(self) -> str:
        return reverse("posts:detail", args=[self.id])

    def get_breadcrumbs(self) -> List[Tuple[str, str]]:
        return [
            (reverse("activities:stream"), _("Home")),
            (reverse("posts:list"), _("Posts")),
            (self.get_absolute_url(), smart_text(self)),
        ]

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}

    def notify(self, created: bool) -> List[Notification]:
        notifications: List[Notification] = []
        # notify anyone @mentioned in the description
        if self.description and (
            created or self.description_tracker.changed()
        ):
            notifications += [
                Notification(
                    content_object=self,
                    actor=self.owner,
                    community=self.community,
                    recipient=recipient,
                    verb="mentioned",
                )
                for recipient in self.community.members.matches_usernames(
                    self.description.extract_mentions()
                ).exclude(pk=self.owner_id)
            ]
        # notify all community moderators
        verb = "created" if created else "updated"
        notifications += [
            Notification(
                content_object=self,
                recipient=recipient,
                actor=self.owner,
                community=self.community,
                verb=verb,
            )
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        Notification.objects.bulk_create(notifications)
        return notifications
