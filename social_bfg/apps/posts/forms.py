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
                "data-action": " ".join(
                    [
                        f"{event}->opengraph-preview#validate"
                        for event in ("keyup", "change", "paste")
                    ]
                ),
            }
        )

    def get_context(self, name, value, attrs):
        data = super().get_context(name, value, attrs)

        data.update(
            {
                "preview": {
                    "image": self.preview_image,
                    "description": self.preview_description,
                }
            }
        )
        return data


class PostForm(ActivityForm):
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

        self.fields["url"].label = _("URL")
        self.fields["url"].widget = OpengraphPreviewInput(
            preview_image=self.instance.opengraph_image,
            preview_description=self.instance.opengraph_description,
        )
        self.fields["url"].help_text = _(
            "You can attach an image and/or description from the webpage to this post by "
            "clicking the Download button on the right."
        )

        self.fields["opengraph_image"].widget = forms.HiddenInput()
        self.fields["opengraph_description"].widget = forms.HiddenInput()

        for field in ("title", "opengraph_image", "opengraph_description", "url"):
            data_targets = (
                self.fields[field].widget.attrs.get("data-target", "").split(" ")
            )
            data_targets.append("opengraph-preview.subscriber")
            self.fields[field].widget.attrs["data-target"] = " ".join(data_targets)
