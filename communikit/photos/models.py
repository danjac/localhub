# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from model_utils import FieldTracker

from sorl.thumbnail import ImageField

from communikit.activities.models import Activity
from communikit.comments.models import Comment
from communikit.flags.models import Flag
from communikit.likes.models import Like
from communikit.notifications.models import Notification


class Photo(Activity):

    title = models.CharField(max_length=300)
    image = ImageField(upload_to="photos")

    description_tracker = FieldTracker(["description"])

    comments = GenericRelation(Comment, related_query_name="post")
    flags = GenericRelation(Flag, related_query_name="post")
    likes = GenericRelation(Like, related_query_name="post")
    notifications = GenericRelation(Notification, related_query_name="post")

    url_prefix = "photos"

    def __str__(self) -> str:
        return self.title

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}
