# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import ImageField

from localhub.activities.models import Activity
from localhub.db.search import SearchIndexer


class Photo(Activity):
    class License(models.TextChoices):
        ATTRIBUTION = "by", _("Attribution")
        ATTRIBUTION_SHAREALIKE = "by-sa", _("Attribution ShareAlike")
        ATTRIBUTION_NODERIVS = "by-nd", _("Attribution NoDerivs")
        ATTRIBUTION_NONCOMMERCIAL = "by-nc", _("Attribution NonCommercial")
        ATTRIBUTION_NONCOMMERCIAL_SHAREALIKE = (
            "by-nc-sa",
            _("Attribution NonCommercial ShareAlike"),
        )
        ATTRIBUTION_NONCOMMERCIAL_NODERIVS = (
            "by-nc-nd",
            _("Attribution NonCommercial NoDerivs"),
        )

    RESHARED_FIELDS = Activity.RESHARED_FIELDS + (
        "image",
        "artist",
        "original_url",
        "cc_license",
        "latitude",
        "longitude",
    )

    image = ImageField(
        upload_to="photos",
        verbose_name=_("Photo"),
        help_text=_(
            "For best results, photos should be no larger than 1MB. "
            "If the image is too large it will not be accepted."
        ),
    )

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    artist = models.CharField(max_length=100, blank=True)
    original_url = models.URLField(max_length=500, null=True, blank=True)
    cc_license = models.CharField(
        max_length=10,
        choices=License.choices,
        null=True,
        blank=True,
        verbose_name="Creative Commons license",
    )

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "description"), ("C", "artist")
    )

    def __str__(self):
        return self.title or _("Photo")

    def has_attribution(self):
        return any((self.artist, self.original_url, self.cc_license))

    def has_map(self):
        return all((self.latitude, self.longitude))
