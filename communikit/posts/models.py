from django.db import models
from django.urls import reverse

from communikit.activities.models import Activity
from communikit.markdown.fields import MarkdownField
from communikit.notifications.models import Notification


class Post(Activity):

    title = models.CharField(max_length=300, blank=True)
    description = MarkdownField(blank=True)
    url = models.URLField(blank=True)

    def __str__(self) -> str:
        return self.title or self.url

    def get_absolute_url(self) -> str:
        return reverse("posts:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())

    def search_index_components(self):
        return {"A": self.title, "B": self.description}


class PostNotification(Notification):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
