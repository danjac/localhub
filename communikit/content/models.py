from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from communikit.communities.models import Community


class Post(TimeStampedModel):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    title = models.CharField(blank=True, max_length=255)

    description = MarkdownxField()

    published = models.DateTimeField(null=True, blank=True)

    objects = InheritanceManager()

    @property
    def markdown(self) -> str:
        # TBD apply bleach!
        return mark_safe(markdownify(self.description))
