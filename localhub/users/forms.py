# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "name",
            "avatar",
            "language",
            "show_sensitive_content",
            "show_embedded_content",
            "home_page_filters",
            "email_preferences",
            "default_timezone",
            "bio",
        )
        widgets = {
            "email_preferences": forms.CheckboxSelectMultiple,
            "home_page_filters": forms.CheckboxSelectMultiple,
        }
        help_texts = {
            "home_page_filters": _(
                "Blocked users and tags will not be shown."
            ),
            "show_sensitive_content": _(
                "Sensitive content will be hidden by default. "
                "If you wish to remove sensitive content completely "
                "from your feeds, you can block specific tags such as #nsfw."
            ),
            "show_embedded_content": _(
                "If you have enabled Do Not Track in your browser, we will "
                "hide content such as YouTube videos and Twitter and Facebook "
                "posts by default. Enabling this setting "
                "ensures embedded content will always be shown on this site."
            ),
        }
