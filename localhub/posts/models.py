# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
from bs4 import BeautifulSoup
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext as _

from localhub.activities.models import Activity
from localhub.activities.oembed import bootstrap_oembed
from localhub.activities.utils import get_domain, is_image_url, is_url
from localhub.comments.models import Comment
from localhub.common.db.search import SearchIndexer
from localhub.common.db.tracker import Tracker
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification

_oembed_registry = bootstrap_oembed()

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
)


class Post(Activity):

    RESHARED_FIELDS = ("title", "description", "url")

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(max_length=500, blank=True)

    # metadata fetched from URL if available

    metadata_image = models.URLField(max_length=500, blank=True)
    metadata_description = models.TextField(blank=True)

    comments = GenericRelation(Comment, related_query_name="post")
    flags = GenericRelation(Flag, related_query_name="post")
    likes = GenericRelation(Like, related_query_name="post")
    notifications = GenericRelation(Notification, related_query_name="post")

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
        Looks for og/twitter title, description and image if available and
        title and/or description missing.

        If no title found then uses URL subdomain by default.

        No action if post does not have a URL.
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
