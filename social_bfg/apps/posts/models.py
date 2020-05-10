# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.db import models
from django.utils.translation import gettext as _

# Social-BFG
from social_bfg.apps.activities.models import Activity
from social_bfg.common.db.search.indexer import SearchIndexer
from social_bfg.common.utils.http import get_domain, is_https, is_image_url


class Post(Activity):

    RESHARED_FIELDS = Activity.RESHARED_FIELDS + [
        "opengraph_description",
        "opengraph_image",
        "url",
    ]

    INDEXABLE_DESCRIPTION_FIELDS = Activity.INDEXABLE_DESCRIPTION_FIELDS + [
        "opengraph_description",
    ]

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(max_length=500, blank=True)

    # metadata fetched from URL if available

    opengraph_image = models.URLField(max_length=500, blank=True)
    opengraph_description = models.TextField(blank=True)

    search_indexer = SearchIndexer(("A", "title"), ("B", "indexable_description"))

    def __str__(self):
        return self.title or self.get_domain() or _("Post")

    def get_domain(self):
        return get_domain(self.url) or ""

    def get_opengraph_image_if_safe(self):
        """
        Returns metadata image if it is an https URL and a valid image extension.
        Otherwise returns empty string.
        """
        return (
            self.opengraph_image
            if is_https(self.opengraph_image) and is_image_url(self.opengraph_image)
            else ""
        )
