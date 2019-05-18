from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from communikit.activities.models import Activity
from communikit.likes.models import Like
from communikit.markdown.fields import MarkdownField


class Comment(TimeStampedModel):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    content = MarkdownField()

    likes = GenericRelation(Like, related_query_name="comment")

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())
