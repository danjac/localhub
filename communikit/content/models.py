import bleach

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe

from bleach.linkifier import LinkifyFilter

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from communikit.communities.models import Community


ALLOWED_TAGS = bleach.ALLOWED_TAGS + ["p", "h1", "h2", "h3", "h4", "h5", "h6"]

cleaner = bleach.Cleaner(ALLOWED_TAGS, filters=[LinkifyFilter])


class Post(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    title = models.CharField(blank=True, max_length=255)

    description = MarkdownxField()

    published = models.DateTimeField(null=True, blank=True)

    objects = InheritanceManager()

    def __str__(self) -> str:
        return self.title or str(f"Post: {self.id}")

    def get_absolute_url(self) -> str:
        return "http://{}{}".format(
            self.community.domain, reverse("content:detail", args=[self.id])
        )

    def markdown(self) -> str:
        return mark_safe(cleaner.clean(markdownify(self.description)))
