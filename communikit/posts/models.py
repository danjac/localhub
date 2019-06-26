# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict, Optional

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext as _

from model_utils import FieldTracker

from communikit.activities.models import Activity
from communikit.activities.utils import get_domain
from communikit.comments.models import Comment
from communikit.flags.models import Flag
from communikit.likes.models import Like
from communikit.notifications.models import Notification


class Post(Activity):

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(blank=True)

    comments = GenericRelation(Comment, related_query_name="post")
    flags = GenericRelation(Flag, related_query_name="post")
    likes = GenericRelation(Like, related_query_name="post")
    notifications = GenericRelation(Notification, related_query_name="post")

    description_tracker = FieldTracker(["description"])

    def __str__(self) -> str:
        return self.title or self.get_domain() or _("Post")

    def get_domain(self) -> Optional[str]:
        return get_domain(self.url)

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}
