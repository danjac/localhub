from django.conf import settings
from django.db import models
from django.urls import reverse

from model_utils.models import TimeStampedModel

from communikit.activities.models import Activity
from communikit.markdown.fields import MarkdownField


class CommentQuerySet(models.QuerySet):
    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(num_likes=models.Count("like"))

    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        if user.is_authenticated:
            return self.annotate(
                has_liked=models.Exists(
                    Like.objects.filter(
                        user=user, activity=models.OuterRef("pk")
                    )
                )
            )
        return self.annotate(
            has_liked=models.Value(False, output_field=models.BooleanField())
        )


class Comment(TimeStampedModel):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    content = MarkdownField()

    objects = CommentQuerySet.as_manager()

    def get_absolute_url(self) -> str:
        return reverse("comments:detail", args=[self.id])

    def get_permalink(self) -> str:
        return self.activity.community.domain_url(self.get_absolute_url())


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "comment")
