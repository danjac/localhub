# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.utils.translation import gettext as _

from localhub.activities.models import Activity
from localhub.db.search import SearchIndexer
from localhub.db.tracker import Tracker
from localhub.oembed import bootstrap_oembed
from localhub.utils.urls import get_domain, is_image_url

from .html_parser import parse_metadata_from_url

_oembed_registry = bootstrap_oembed()


class Post(Activity):

    RESHARED_FIELDS = (
        "description",
        "metadata_description",
        "metadata_image",
        "title",
        "url",
    )

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(max_length=500, blank=True)

    # metadata fetched from URL if available

    metadata_image = models.URLField(max_length=500, blank=True)
    metadata_description = models.TextField(blank=True)

    url_tracker = Tracker(["url"])

    search_indexer = SearchIndexer(("A", "title"), ("B", "indexable_description"))

    def __str__(self):
        return self.title or self.get_domain() or _("Post")

    def get_domain(self):
        return get_domain(self.url)

    @property
    def indexable_description(self):
        return " ".join(
            [value for value in (self.description, self.metadata_description) if value]
        )

    def is_oembed(self):
        if not self.url:
            return False
        return _oembed_registry.provider_for_url(self.url) is not None

    def get_metadata_image_if_safe(self):
        """
        Returns metadata image if it is an https URL and a valid image extension.
        Otherwise returns empty string.
        """
        return (
            self.metadata_image
            if self.metadata_image.startswith("https://")
            and is_image_url(self.metadata_image)
            else ""
        )

    def fetch_metadata_from_url(self, commit=True):
        """
        Tries to fetch image/description/title from metadata in the target
        URL.

        If present will set the `title`, `metadata_description` and
        `metadata_image` fields from values extracted from the HTML.

        If URL is empty or the page does not return valid HTML or tags
        then metadata_description and metadata_image are set to empty. If
        not set the title will be set to the domain of the URL.
        """

        title, image, description = parse_metadata_from_url(self.url)

        self.metadata_image = image or ""
        self.metadata_description = description or ""

        if not self.title:
            self.title = (title or self.get_domain())[:300]

        if commit:
            self.save()
