# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.activities.forms import ActivityForm

from .models import Post


class OpengraphPreviewInput(forms.URLInput):
    template_name = "posts/includes/widgets/opengraph_preview.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs.update({"data-target": "opengraph-preview.input"})


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
        widgets = {"url": OpengraphPreviewInput}
        labels = {"url": _("URL")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].required = True

        self.fields["title"].widget.attrs.update(
            {
                "data-controller": "opengraph-preview",
                "data-target": "opengraph-preview.input",
                "data-opengraph-preview-subscriber": "title",
            }
        )

        self.fields["opengraph_image"].widget = forms.HiddenInput(
            attrs={
                "data-controller": "opengraph-preview",
                "data-target": "opengraph-preview.input",
                "data-opengraph-preview-subscriber": "image",
            }
        )
        self.fields["opengraph_description"].widget = forms.HiddenInput(
            attrs={
                "data-controller": "opengraph-preview",
                "data-target": "opengraph-preview.input",
                "data-opengraph-preview-subscriber": "description",
            }
        )
