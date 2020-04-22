# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.utils.http import URLResolver
from localhub.utils.scraper import HTMLScraper

from .models import Post


class PostForm(ActivityForm):

    clear_opengraph_data = forms.BooleanField(
        required=False, label=_("Clear OpenGraph content from post")
    )

    fetch_opengraph_data = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Fetch OpenGraph and other content from URL if available"),
    )

    class Meta(ActivityForm.Meta):
        model = Post
        fields = (
            "title",
            "hashtags",
            "mentions",
            "url",
            "clear_opengraph_data",
            "fetch_opengraph_data",
            "description",
            "allow_comments",
            "opengraph_image",
            "opengraph_description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["url"].label = _("URL")
        self.fields["title"].help_text = _("Optional if URL provided")
        self.fields["opengraph_image"].widget = forms.HiddenInput()
        self.fields["opengraph_description"].widget = forms.HiddenInput()

        if self.instance.opengraph_image or self.instance.opengraph_description:
            self.initial["fetch_opengraph_data"] = False
            self.fields["fetch_opengraph_data"].label = _(
                "Re-fetch OpenGraph and other content from URL if available"
            )
        else:
            del self.fields["clear_opengraph_data"]

    def clean(self):
        cleaned_data = super().clean()
        try:
            cleaned_data.update(self.scrape_html(**cleaned_data))
        except HTMLScraper.Invalid:
            self.add_error(
                "url",
                _(
                    "This URL appears to be either inaccessible, or we are unable to find any metadata in the content. "
                    "You can uncheck the 'Fetch OpenGraph' box and just add your own title and description to this post."
                ),
            )
            return cleaned_data

        title = cleaned_data.get("title")

        if not title:
            self.add_error(
                "title", _("Title must be provided if not available from URL")
            )

        return cleaned_data

    def scrape_html(
        self,
        *,
        title="",
        url="",
        fetch_opengraph_data=False,
        clear_opengraph_data=False,
        **cleaned_data
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
            title = title or url_resolver.filename
            clear_opengraph_data = True

        if clear_opengraph_data:
            data.update({"opengraph_image": "", "opengraph_description": ""})
            fetch_opengraph_data = False

        # run scraper if missing title or explicitly fetching OpenGraph data.
        if fetch_opengraph_data or not title:
            scraper = HTMLScraper.from_url(url_resolver.url)
            title = title or scraper.title or url_resolver.filename or ""
            # ensure we don't have too long image
            if scraper.image and len(scraper.image) > 500:
                scraper.image = ""
            if fetch_opengraph_data:
                data.update(
                    {
                        "opengraph_image": scraper.image or "",
                        "opengraph_description": scraper.description or "",
                    }
                )

        data.update({"title": title[:300]})
        return data
