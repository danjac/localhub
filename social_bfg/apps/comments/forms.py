# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        labels = {"content": _("Comment")}
