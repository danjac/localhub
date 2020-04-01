# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm
from localhub.utils.http import is_image_url, resolve_url

from .html_scraper import HTMLScraper
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
            "additional_tags",
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
            self.add_error("url", _("This URL appears to be invalid."))
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
        if clear_opengraph_data:
            return {"opengraph_image": "", "opengraph_description": ""}

        if not url:
            return {}

        url = resolve_url(url)

        data = {"url": url}

        if is_image_url(url):
            """
            Image URLs are OK, as they are just rendered directly in oembed
            elements.
            """
            return data

        if not title or fetch_opengraph_data:
            scraper = HTMLScraper.from_url(url)
            data.update({"title": (title or scraper.title)[:300]})
            if fetch_opengraph_data:
                data.update(
                    {
                        "opengraph_image": scraper.image or "",
                        "opengraph_description": scraper.description or "",
                    }
                )
            return data
        return {}
