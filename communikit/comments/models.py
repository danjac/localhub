from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from model_utils.models import TimeStampedModel


from communikit.content.models import Post
from communikit.content.markdown import markdownify


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    content = MarkdownxField()

    def markdown(self) -> str:
        return mark_safe(markdownify(self.content))

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.post.community.domain_url(self.get_absolute_url())
