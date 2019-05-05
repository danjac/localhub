from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, IntegrityError
from django.urls import reverse
from django.utils.safestring import mark_safe

from markdownx.models import MarkdownxField

from model_utils.models import TimeStampedModel


from communikit.content.markdown import markdownify
from communikit.content.models import Post
from communikit.likes.models import Like


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    content = MarkdownxField()

    likes = GenericRelation(Like, related_query_name="comment")

    def markdown(self) -> str:
        return mark_safe(markdownify(self.content))

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.post.community.domain_url(self.get_absolute_url())

    def like(self, user: settings.AUTH_USER_MODEL) -> bool:
        """
        If like already exists, deletes the like, otherwise
        creates new one. Returns whether user likes object or not.
        """
        try:
            self.likes.get(user=user).delete()
            return False
        except ObjectDoesNotExist:
            try:
                self.likes.create(user=user)
            except IntegrityError:
                pass
        return True
