# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.utils.http import URLResolver
from localhub.utils.scraper import HTMLScraper

from .models import Post


class OpengraphPreviewInput(forms.URLInput):
    template_name = "posts/includes/opengraph_preview.html"


class PostForm(ActivityForm):

    clear_opengraph_data = forms.BooleanField(
        required=False, label=_("Clear OpenGraph content from post")
    )

    class Meta(ActivityForm.Meta):
        model = Post
        fields = (
            "title",
            "hashtags",
            "mentions",
            "url",
            "clear_opengraph_data",
            "description",
            "allow_comments",
            "opengraph_image",
            "opengraph_description",
        )
        widgets = {"url": OpengraphPreviewInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["url"].label = _("URL")
        self.fields["title"].help_text = _("Optional if URL provided")
        self.fields["opengraph_image"].widget = forms.HiddenInput()
        self.fields["opengraph_description"].widget = forms.HiddenInput()

        if (
            not self.instance.opengraph_image
            and not self.instance.opengraph_description
        ):
            del self.fields["clear_opengraph_data"]

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.update(self.scrape_html(**cleaned_data))

        if not cleaned_data.get("title"):
            self.add_error(
                "title", _("Title must be provided if not available from URL")
            )

        return cleaned_data

    def scrape_html(
        self, *, title="", url="", clear_opengraph_data=False, **cleaned_data
    ):
        try:
            url_resolver = URLResolver.from_url(url, resolve=True)
        except URLResolver.Invalid:
            return {}

        data = {"url": url_resolver.url}

        if url_resolver.is_image:
            """
            Image URLs are OK, as they are just rendered directly in oembed
            elements. No need to check for OpenGraph or other HTML data.
            """
            data.update(
                {
                    "title": title or url_resolver.filename,
                    "opengraph_image": "",
                    "opengraph_description": "",
                }
            )
            return data

        if clear_opengraph_data:
            data.update({"opengraph_image": "", "opengraph_description": ""})
            return data

        # run scraper if missing title or explicitly fetching OpenGraph data.
        try:
            scraper = HTMLScraper.from_url(url_resolver.url)
        except HTMLScraper.Invalid:
            return data

        title = title or scraper.title or url_resolver.filename or ""
        # ensure we don't have too long image
        if scraper.image and len(scraper.image) > 500:
            scraper.image = ""

        data.update(
            {
                "opengraph_image": scraper.image or "",
                "opengraph_description": scraper.description or "",
                "title": title[:300],
            }
        )

        return data
