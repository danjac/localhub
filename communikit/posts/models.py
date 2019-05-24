# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List

from django.db import models
from django.urls import reverse

from model_utils import FieldTracker

from communikit.activities.models import Activity
from communikit.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class Post(Activity):

    title = models.CharField(max_length=300, blank=True)
    description = MarkdownField(blank=True)
    url = models.URLField(blank=True)

    description_tracker = FieldTracker(["description"])

    def __str__(self) -> str:
        return self.title or self.url

    def get_absolute_url(self) -> str:
        return reverse("posts:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}

    def notify(self, created: bool) -> List["PostNotification"]:
        notifications = []
        # notify anyone @mentioned in the description
        if self.description and (
            created or self.description_tracker.changed()
        ):
            notifications += [
                PostNotification(
                    post=self, recipient=recipient, verb="mentioned"
                )
                for recipient in self.community.members.matches_usernames(
                    self.description.extract_mentions()
                ).exclude(pk=self.owner_id)
            ]
        # notify all community moderators
        verb = "created" if created else "updated"
        notifications += [
            PostNotification(post=self, recipient=recipient, verb=verb)
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        PostNotification.objects.bulk_create(notifications)
        return notifications


class PostNotification(Notification):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="notifications"
    )
