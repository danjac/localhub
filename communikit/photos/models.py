# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Dict

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices, FieldTracker

from sorl.thumbnail import ImageField

from communikit.activities.models import Activity
from communikit.comments.models import Comment
from communikit.flags.models import Flag
from communikit.likes.models import Like
from communikit.notifications.models import Notification


class Photo(Activity):

    CC_LICENSES = Choices(
        ("by", _("Attribution")),
        ("by-sa", _("Attribution ShareAlike")),
        ("by-nd", _("Attribution NoDerivs")),
        ("by-nc", _("Attribution NonCommercial")),
        ("by-nc-sa", _("Attribution NonCommercial ShareAlike")),
        ("by-nc-nd", _("Attribution NonCommercial NoDerivs")),
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
        verbose_name="Creative Commons License",
    )

    comments = GenericRelation(Comment, related_query_name="photo")
    flags = GenericRelation(Flag, related_query_name="photo")
    likes = GenericRelation(Like, related_query_name="photo")
    notifications = GenericRelation(Notification, related_query_name="photo")

    description_tracker = FieldTracker(["description"])

    def __str__(self) -> str:
        return self.title

    def search_index_components(self) -> Dict[str, str]:
        return {"A": self.title, "B": self.description}

    def has_attribution(self) -> bool:
        return any((self.artist, self.original_url, self.cc_license))
