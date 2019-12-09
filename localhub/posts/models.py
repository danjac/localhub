# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from bs4 import BeautifulSoup
from django.db import models
from django.utils.translation import gettext as _

from localhub.activities.models import Activity
from localhub.db.search import SearchIndexer
from localhub.db.tracker import Tracker
from localhub.oembed import bootstrap_oembed
from localhub.utils.urls import get_domain, is_image_url, is_url

_oembed_registry = bootstrap_oembed()

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


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

        def _save_if_commit():
            if commit:
                self.save()

        if not self.url:
            self.metadata_description = ""
            self.metadata_image = ""
            return _save_if_commit()

        try:
            response = requests.get(self.url, headers={"User-Agent": USER_AGENT})
            if not response.ok or "text/html" not in response.headers.get(
                "Content-Type", ""
            ):
                raise ValueError
        except (requests.RequestException, ValueError):
            if not self.title:
                self.title = self.get_domain()[:300]
            self.metadata_description = ""
            self.metadata_image = ""
            return _save_if_commit()

        soup = BeautifulSoup(response.content, "html.parser")

        if not self.title:
            title = soup.find("meta", attrs={"property": "og:title"}) or soup.find(
                "meta", attrs={"name": "twitter:title"}
            )

            if title and "content" in title.attrs:
                self.title = title["content"]
            else:
                self.title = soup.title.string if soup.title else self.get_domain()

            self.title = self.title.strip()[:300]

        self.metadata_image = ""
        try:
            image = soup.find("meta", attrs={"property": "og:image"}).attrs["content"]
            if len(image) < 501 and is_url(image) and is_image_url(image):
                self.metadata_image = image
        except (AttributeError, KeyError):
            pass

        description = soup.find(
            "meta", attrs={"property": "og:description"}
        ) or soup.find("meta", attrs={"name": "twitter:description"})
        if description and "content" in description.attrs:
            self.metadata_description = description.attrs["content"]
        else:
            self.metadata_description = ""

        _save_if_commit()
