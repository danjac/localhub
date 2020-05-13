# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import forms
from django.utils.translation import gettext as _

# Social-BFG
from social_bfg.apps.activities.forms import ActivityForm

# Local
from .models import Post


class OpengraphPreviewInput(forms.URLInput):
    template_name = "posts/includes/widgets/opengraph_preview.html"

    def __init__(self, attrs=None, preview_description=None, preview_image=None):
        super().__init__(attrs)
        self.preview_image = preview_image
        self.preview_description = preview_description
        self.attrs.update(
            {
                "data-target": "opengraph-preview.input",
                "data-action": "paste->opengraph-preview#validate keyup->opengraph-preview#validate change->opengraph-preview#validate",
            }
        )

    def get_context(self, name, value, attrs):
        data = super().get_context(name, value, attrs)

        data.update(
            {
                "has_preview": self.preview_description or self.preview_image,
                "preview_description": self.preview_description,
                "preview_image": self.preview_image,
            }
        )
        return data


class PostForm(ActivityForm):
    # TBD : hidden opengraph_title input, so can be overriden????
    class Meta(ActivityForm.Meta):
        model = Post
        fields = (
            "title",
            "url",
            "hashtags",
            "mentions",
            "description",
            "allow_comments",
            "opengraph_image",
            "opengraph_description",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].required = True

        self.fields["title"].widget.attrs.update(
            {
                "data-target": self.fields["title"].widget.attrs["data-target"]
                + " opengraph-preview.listener",
                "data-opengraph-preview-listener-value": "title",
            }
        )

        self.fields["url"].label = _("URL")
        self.fields["url"].widget = OpengraphPreviewInput(
            preview_image=self.instance.opengraph_image,
            preview_description=self.instance.opengraph_description,
        )

        self.fields["opengraph_image"].widget = forms.HiddenInput(
            attrs={
                "data-target": "opengraph-preview.listener",
                "data-opengraph-preview-listener-value": "image",
            }
        )
        self.fields["opengraph_description"].widget = forms.HiddenInput(
            attrs={
                "data-target": "opengraph-preview.listener",
                "data-opengraph-preview-listener-value": "description",
            }
        )
