from typing import Dict, List

from django.db import models
from django.utils.safestring import mark_safe

from sorl.thumbnail import ImageField

from communikit.activities.models import Activity
from communikit.markdown.utils import linkify_hashtags
from communikit.notifications.models import Notification


class Photo(Activity):

    title = models.CharField(max_length=300)
    image = ImageField(upload_to="photos/")
    tags = models.CharField(max_length=300, blank=True)

    def __str__(self) -> str:
        return self.title

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
