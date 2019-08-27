# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext as _

from localhub.activities.models import Activity
from localhub.activities.utils import get_domain
from localhub.comments.models import Comment
from localhub.core.utils.search import SearchIndexer
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification


class Post(Activity):

    RESHARED_FIELDS = ("title", "description", "url")

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(blank=True)

    comments = GenericRelation(Comment, related_query_name="post")
    flags = GenericRelation(Flag, related_query_name="post")
    likes = GenericRelation(Like, related_query_name="post")
    notifications = GenericRelation(Notification, related_query_name="post")

    search_indexer = SearchIndexer(("A", "title"), ("B", "description"))

    def __str__(self):
        return self.title or self.get_domain() or _("Post")

    def get_domain(self):
        return get_domain(self.url)
