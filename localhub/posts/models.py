# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext as _

from bs4 import BeautifulSoup

from localhub.activities.oembed import bootstrap_oembed
from localhub.activities.models import Activity
from localhub.activities.utils import get_domain
from localhub.comments.models import Comment
from localhub.common.db.search import SearchIndexer
from localhub.common.db.tracker import Tracker
from localhub.flags.models import Flag
from localhub.likes.models import Like
from localhub.notifications.models import Notification

_oembed_registry = bootstrap_oembed()


class Post(Activity):

    RESHARED_FIELDS = ("title", "description", "url")

    title = models.CharField(max_length=300, blank=True)
    url = models.URLField(blank=True)

    # metadata fetched from URL if available

    metadata_image = models.URLField(blank=True)
    metadata_description = models.TextField(blank=True)

    comments = GenericRelation(Comment, related_query_name="post")
    flags = GenericRelation(Flag, related_query_name="post")
    likes = GenericRelation(Like, related_query_name="post")
    notifications = GenericRelation(Notification, related_query_name="post")

    url_tracker = Tracker(["url"])

    search_indexer = SearchIndexer(
        ("A", "title"), ("B", "indexable_description")
    )

    def __str__(self):
        return self.title or self.get_domain() or _("Post")

    def get_domain(self):
        return get_domain(self.url)

    @property
    def indexable_description(self):
        return " ".join(
            [
                value
                for value in (self.description, self.metadata_description)
                if value
            ]
        )

    def is_oembed(self):
        if not self.url:
            return False
        return _oembed_registry.provider_for_url(self.url) is not None

    def fetch_metadata_from_url(self):
        """
        Looks for og/twitter title, description and image if available and
        title and/or description missing.

        If no title found then uses URL subdomain by default.

        No action if post does not have a URL.
        """

        update_fields = ["title", "metadata_description", "metadata_image"]

        if not self.url:
            self.metadata_description = ""
            self.metadata_image = ""
            self.save(update_fields=update_fields)
            return

        response = requests.get(self.url)
        if not response.ok or "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            if not self.title:
                self.title = self.get_domain()[:300]
            self.metadata_description = ""
            self.metadata_image = ""
            self.save(update_fields=update_fields)
            return

        soup = BeautifulSoup(response.content, "html.parser")

        if not self.title:
            title = soup.find(
                "meta", attrs={"property": "og:title"}
            ) or soup.find("meta", attrs={"name": "twitter:title"})

            if title and "content" in title.attrs:
                self.title = title["content"]
            else:
                self.title = (
                    soup.title.string if soup.title else self.get_domain()
                )

            self.title = self.title.strip()[:300]

        image = soup.find("meta", attrs={"property": "og:image"})
        if image and "content" in image.attrs:
            self.metadata_image = image.attrs["content"]
        else:
            self.metadata_image = ""

        description = soup.find(
            "meta", attrs={"property": "og:description"}
        ) or soup.find("meta", attrs={"name": "twitter:description"})
        if description and "content" in description.attrs:
            self.metadata_description = description.attrs["content"]
        else:
            self.metadata_description = ""

        self.save(update_fields=update_fields)
