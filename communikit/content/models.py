from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from model_utils.managers import InheritanceManager
from model_utils.models import TimeStampedModel

from communikit.communities.models import Community
from communikit.content.markdown import markdownify


class Post(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    title = models.CharField(blank=True, max_length=255)

    url = models.URLField(blank=True)

    description = MarkdownxField(blank=True)

    published = models.DateTimeField(null=True, blank=True)

    objects = InheritanceManager()

    def __str__(self) -> str:
        return self.title or str(f"Post: {self.id}")

    def get_absolute_url(self) -> str:
        return reverse("content:detail", args=[self.id])

    def get_permalink(self) -> str:
        return f"http://{self.community.domain}{self.get_absolute_url()}"

    def markdown(self) -> str:
        return mark_safe(markdownify(self.description))
