import collections

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from model_utils.models import TimeStampedModel


class LikeManager(models.Manager):
    def user_has_liked(
        self, user: settings.AUTH_USER_MODEL, obj: models.Model
    ) -> bool:
        if user.is_anonymous:
            return False
        # cache for all likes/instances for this user, so we do just
        # one db lookup
        if not hasattr(user, "_likes_cache"):
            user._likes_cache = collections.defaultdict(set)
            for like in self.filter(user=user).select_related("content_type"):
                user._likes_cache[like.content_type.name].add(like.object_id)
        # this call is also cached
        content_type = ContentType.objects.get_for_model(obj)
        return obj.id in user._likes_cache.get(content_type.name, set())


class Like(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = LikeManager()

    class Meta:
        unique_together = ("user", "content_type", "object_id")
