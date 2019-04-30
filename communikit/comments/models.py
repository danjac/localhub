from django.db import models
from django.conf import settings
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from model_utils.models import TimeStampedModel


from communikit.content.models import Post
from communikit.content.markdown import markdownify


class Comment(TimeStampedModel):
    # set null: if original post is deleted
    # we can still keep the comment
    post = models.ForeignKey(
        Post, null=True, on_delete=models.SET_NULL, db_index=True
    )
    parent = models.ForeignKey(
        "self", null=True, on_delete=models.SET_NULL, db_index=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    content = MarkdownxField()

    def markdown(self) -> str:
        return mark_safe(markdownify(self.content))
