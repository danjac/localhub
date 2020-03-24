# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import TypeaheadInput

from .models import Post
from .opengraph import Opengraph


class PostForm(forms.ModelForm):

    clear_opengraph_data = forms.BooleanField(
        required=False, label=_("Clear OpenGraph data from post")
    )

    fetch_opengraph_data = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Fetch OpenGraph data from URL if available"),
    )

    class Meta:
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
        labels = {"title": _("Title"), "url": _("URL"), "additional_tags": _("Tags")}
        widgets = {
            "title": TypeaheadInput,
            "additional_tags": TypeaheadInput(search_mentions=False),
            "opengraph_image": forms.HiddenInput,
            "opengraph_description": forms.HiddenInput,
        }
        help_texts = {
            "title": _("Optional if URL provided"),
            "additional_tags": _(
                "Hashtags can also be added to title and description."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.opengraph_image or self.instance.opengraph_description:
            self.initial["fetch_opengraph_data"] = False
            self.fields["fetch_opengraph_data"].label = _(
                "Re-fetch OpenGraph data from URL if available"
            )
        else:
            del self.fields["clear_opengraph_data"]

    def clean(self):
        cleaned_data = super().clean()

        title = cleaned_data.get("title")
        url = cleaned_data.get("url")

        if not any((title, url)):
            raise forms.ValidationError(_("Either title or URL must be provided"))

        if cleaned_data.get("clear_opengraph_data"):
            cleaned_data["opengraph_image"] = ""
            cleaned_data["opengraph_description"] = ""
        elif url and (not title or cleaned_data["fetch_opengraph_data"]):
            og = Opengraph.from_url(url)
            cleaned_data["url"] = og.url or ""

            if not title:
                cleaned_data["title"] = og.title[:300]

            if cleaned_data["fetch_opengraph_data"]:
                cleaned_data["opengraph_image"] = og.image or ""
                cleaned_data["opengraph_description"] = og.description or ""

        return cleaned_data
