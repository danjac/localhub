# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import ClearableImageInput

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
            # "language",
            "bio",
            "show_sensitive_content",
            "show_embedded_content",
            "activity_stream_filters",
            "send_email_on_message",
            "send_webpush_on_message",
            "send_email_on_notification",
            "send_webpush_on_notification",
            "notification_preferences",
        )
        widgets = {
            "notification_preferences": forms.CheckboxSelectMultiple,
            "activity_stream_filters": forms.CheckboxSelectMultiple,
            "avatar": ClearableImageInput,
        }

        labels = {
            "send_email_on_message": _(
                "Send me an email when I receive a new Direct Message"
            ),
            "send_email_on_notification": _(
                "Send me an email when I receive a new Notification"
            ),
            "send_webpush_on_message": _(
                "Display a browser notification when I receive a new Direct Message"
            ),
            "send_webpush_on_notification": _(
                "Display a browser notification when I receive a new Notification"
            ),
        }
        help_texts = {
            "activity_stream_filters": mark_safe(
                _(
                    "Blocked users and tags will not be shown.<br>"
                    "Content you post yourself will not be filtered."
                )
            ),
            "show_sensitive_content": _(
                "Sensitive content (content containing specific tags as defined by the community admins) "
                "will otherwise be obscured by default but not removed from your feeds. <br>"
                "If you wish to remove sensitive content completely "
                "from your feeds, you can block individual tags (e.g. <b>#nsfw</b>) under the "
                "<a href='%(tags_url)s'>Tags</a> page."
            ),
            "show_embedded_content": _(
                "Show embedded content such as YouTube videos or Instagram or Twitter posts."
            ),
            "send_email_on_notification": mark_safe(
                _(
                    "Select which Notifications you want to receive under <b>Notification preferences</b>."
                )
            ),
            "send_webpush_on_message": _(
                "Click the 'Enable browser notifications' link "
                "in the <a href='%(notifications_url)s'>Notifications</a> page "
                "to grant the required permissions to your browser and device."
            ),
            "send_webpush_on_notification": _(
                "Select which Notifications you receive under <b>Notification preferences</b>.<br>"
                "Click the 'Enable browser notifications' link "
                "in the <a href='%(notifications_url)s'>Notifications</a> page "
                "to grant the required permissions to your browser and device."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in (
            "send_webpush_on_message",
            "send_webpush_on_notification",
            "show_sensitive_content",
        ):
            self.fields[field].help_text = mark_safe(
                self.fields[field].help_text
                % {
                    "notifications_url": reverse("notifications:list"),
                    "tags_url": reverse("activities:tag_list"),
                }
            )
