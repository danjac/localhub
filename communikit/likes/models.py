# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Sequence

from django.db import models

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from communikit.communities.models import Community
from communikit.core.utils.content_types import (
    get_content_type_count_subquery,
    get_content_type_exists,
)


class LikeAnnotationsQuerySetMixin:
    def with_has_liked(
        self, user: settings.AUTH_USER_MODEL
    ) -> models.QuerySet:
        return self.annotate(
            has_liked=get_content_type_exists(
                self.model, Like.objects.filter(user=user)
            )
        )

    def with_num_likes(self) -> models.QuerySet:
        return self.annotate(
            num_likes=get_content_type_count_subquery(
                self.model, Like.objects.all()
            )
        )


class LikeQuerySet(models.QuerySet):
    def for_models(self, *models: Sequence[models.Model]) -> models.QuerySet:
        return self.filter(
            content_type__in=ContentType.objects.get_for_models(
                *models
            ).values()
        )


class Like(models.Model):

    community = models.ForeignKey(
        Community, related_name="+", on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")

    objects = LikeQuerySet.as_manager()
