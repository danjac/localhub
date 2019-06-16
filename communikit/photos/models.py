# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List, Tuple

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _

from sorl.thumbnail import ImageField

from communikit.activities.models import Activity
from communikit.core.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class Photo(Activity):

    title = models.CharField(max_length=300)
    image = ImageField(upload_to="photos")
    description = MarkdownField(blank=True)

    notifications = GenericRelation(Notification, related_query_name="photo")

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("photos:detail", args=[self.id])

    def get_breadcrumbs(self) -> List[Tuple[str, str]]:
        return [
            (reverse("activities:stream"), _("Home")),
            (reverse("photos:list"), _("Photos")),
            (self.get_absolute_url(), smart_text(self)),
        ]

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}

    def notify(self, created: bool) -> List[Notification]:
        notifications: List[Notification] = []
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
