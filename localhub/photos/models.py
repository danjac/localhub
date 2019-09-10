# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from sorl.thumbnail import ImageField

from localhub.activities.models import Activity
from localhub.comments.models import Comment
from localhub.common.db.search import SearchIndexer
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification


class Photo(Activity):

    CC_LICENSES = Choices(
        ("by", _("Attribution")),
        ("by-sa", _("Attribution ShareAlike")),
        ("by-nd", _("Attribution NoDerivs")),
        ("by-nc", _("Attribution NonCommercial")),
        ("by-nc-sa", _("Attribution NonCommercial ShareAlike")),
        ("by-nc-nd", _("Attribution NonCommercial NoDerivs")),
    )

    RESHARED_FIELDS = (
        "title",
        "description",
        "image",
        "artist",
        "original_url",
        "cc_license",
    )

    title = models.CharField(max_length=300)
    image = ImageField(upload_to="photos")

    artist = models.CharField(max_length=100, blank=True)
    original_url = models.URLField(null=True, blank=True)
    cc_license = models.CharField(
        max_length=10,
        choices=CC_LICENSES,
        null=True,
        blank=True,
        verbose_name="Creative Commons license",
    )

    comments = GenericRelation(Comment, related_query_name="photo")
    flags = GenericRelation(Flag, related_query_name="photo")
    likes = GenericRelation(Like, related_query_name="photo")
    notifications = GenericRelation(Notification, related_query_name="photo")

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "description"), ("C", "artist")
    )

    def __str__(self):
        return self.title

    def has_attribution(self):
        return any((self.artist, self.original_url, self.cc_license))
