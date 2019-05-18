from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.likes.models import Like
from communikit.markdown.fields import MarkdownField


class Comment(TimeStampedModel):

    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    content = MarkdownField()

    activity_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    activity_id = models.PositiveIntegerField(db_index=True)
    activity = GenericForeignKey("activity_content_type", "activity_id")

    likes = GenericRelation(Like, related_query_name="comment")

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.community.domain_url(self.get_absolute_url())
