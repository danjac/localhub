# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, List, Tuple

from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from sorl.thumbnail import ImageField

from communikit.activities.models import Activity
from communikit.core.markdown.utils import linkify_hashtags
from communikit.notifications.models import Notification


class Photo(Activity):

    title = models.CharField(max_length=300)
    image = ImageField(upload_to="photos")
    tags = models.CharField(max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("photos:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.resolve_url(self.get_absolute_url())

    def get_breadcrumbs(self) -> List[Tuple[str, str]]:
        return [
            (reverse("activities:stream"), _("Home")),
            (reverse("photos:list"), _("Photos")),
            (self.get_absolute_url(), smart_text(self)),
        ]

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.tags}

    def linkify_tags(self) -> str:
        return mark_safe(linkify_hashtags(self.tags))

    def notify(self, created: bool) -> List["PhotoNotification"]:
        notifications: List[PhotoNotification] = []
        verb = "created" if created else "updated"
        notifications += [
            PhotoNotification(photo=self, recipient=recipient, verb=verb)
            for recipient in self.community.get_moderators().exclude(
                pk=self.owner_id
            )
        ]
        PhotoNotification.objects.bulk_create(notifications)
        return notifications


class PhotoNotification(Notification):

    photo = models.ForeignKey(
        Photo, on_delete=models.CASCADE, related_name="notifications"
    )
