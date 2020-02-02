# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext as _

from localhub.activities.models import Activity
from localhub.db.search import SearchIndexer
from localhub.db.tracker import Tracker
from localhub.oembed import bootstrap_oembed
from localhub.utils.urls import get_domain, is_image_url

from .opengraph_parser import parse_opengraph_data_from_url

_oembed_registry = bootstrap_oembed()


class Post(Activity):

    RESHARED_FIELDS = (
        "description",
        "opengraph_description",
        "opengraph_image",
        "title",
        "url",
    )

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(max_length=500, blank=True)

    # metadata fetched from URL if available

    opengraph_image = models.URLField(max_length=500, blank=True)
    opengraph_description = models.TextField(blank=True)

    url_tracker = Tracker(["url"])

    search_indexer = SearchIndexer(("A", "title"), ("B", "indexable_description"))

    def __str__(self):
        return self.title or self.get_domain() or _("Post")

    def get_domain(self):
        return get_domain(self.url)

    @property
    def indexable_description(self):
        return " ".join(
            [value for value in (self.description, self.opengraph_description) if value]
        )

    def is_oembed(self):
        if not self.url:
            return False
        return _oembed_registry.provider_for_url(self.url) is not None

    def get_opengraph_image_if_safe(self):
        """
        Returns metadata image if it is an https URL and a valid image extension.
        Otherwise returns empty string.
        """
        return (
            self.opengraph_image
            if self.opengraph_image.startswith("https://")
            and is_image_url(self.opengraph_image)
            else ""
        )

    def fetch_opengraph_data_from_url(self, commit=True):
        """
        Tries to fetch image/description/title from metadata in the target
        URL.

        If present will set the `title`, `opengraph_description` and
        `opengraph_image` fields from values extracted from the HTML.

        If URL is empty or the page does not return valid HTML or tags
        then opengraph_description and opengraph_image are set to empty. If
        not set the title will be set to the domain of the URL.
        """

        title, image, description = parse_opengraph_data_from_url(self.url)

        self.opengraph_image = image or ""
        self.opengraph_description = description or ""

        if not self.title:
            self.title = (title or self.get_domain())[:300]

        if commit:
            self.save()
