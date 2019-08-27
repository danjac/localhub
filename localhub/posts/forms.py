# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _


from localhub.posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "url", "description", "allow_comments")
        labels = {"title": _("Title"), "url": _("Link")}
        help_texts = {
            "title": _(
                "If you add a URL in the Link field below and leave the Title "
                "field empty, we will try to automatically fetch a title for "
                "your post from the web page."
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["url"].widget.attrs.update(
            {"placeholder": _("Add a full link here")}
        )

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        url = cleaned_data.get("url")
        if not any((title, url)):
            raise forms.ValidationError(
                _("Either title or URL must be provided")
            )
        return cleaned_data
