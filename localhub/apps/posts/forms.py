# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext as _

from localhub.apps.activities.forms import ActivityForm

from .models import Post


class OpengraphPreviewInput(forms.URLInput):
    # TBD: this feels like the controller should be form-level,
    # not widget. Ditto calendar controls for events.
    template_name = "posts/includes/widgets/opengraph_preview.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs.update(
            {
                "data-target": "opengraph-preview.input",
                "data-action": "opengraph-preview#fetch",
            }
        )


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
        self.fields["url"].widget = OpengraphPreviewInput()

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
