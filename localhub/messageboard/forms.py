# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import Any, Dict, List, Set

from django import forms
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from localhub.communities.models import Community
from localhub.core.forms.widgets import TypeaheadInput
from localhub.core.markdown.utils import extract_mentions
from localhub.messageboard.models import Message


User = get_user_model()


class MessageForm(forms.ModelForm):

    GROUP_CHOICES = (
        ("moderators", _("Community moderators")),
        ("admins", _("Community admins")),
        ("followers", _("People following me")),
        ("everyone", _("All members of this community")),
    )

    individuals = forms.CharField(
        required=False,
        widget=TypeaheadInput(attrs={"rows": 5}, search_hashtags=False),
        label=_("Send to individual recipients"),
        help_text=_(
            "Prefix each name with the @ character to send a message to individual members of the community"  # noqa
        ),
    )

    groups = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=GROUP_CHOICES,
        label=_("Send to people belonging to these groups"),
        help_text=_(
            "All those belonging to the groups you select will receive your message"  # noqa
        ),
    )

    class Meta:
        model = Message
        fields = ("subject", "message")

    def clean(self) -> Dict[str, Any]:
        data = super().clean()
        if not data.get("groups") and not data.get("individuals"):
            raise forms.ValidationError(
                _("You must include at least one group or individual user")
            )
        return data

    def get_recipient_queryset(
        self,
        sender: settings.AUTH_USER_MODEL,
        community: Community,
        groups: List[str],
        mentions: Set[str],
    ) -> models.QuerySet:

        if "everyone" in groups:
            return community.members.all()

        qs = User.objects.none()

        if mentions:
            qs = qs | User.objects.matches_usernames(mentions)

        if "moderators" in groups:
            qs = qs | community.get_moderators()

        if "admins" in groups:
            qs = qs | community.get_admins()

        if "followers" in groups:
            qs = qs | User.objects.followers(sender, community)

        return qs

    def get_recipients(
        self, sender: settings.AUTH_USER_MODEL, community: Community
    ) -> models.QuerySet:

        return (
            self.get_recipient_queryset(
                sender,
                community,
                self.cleaned_data["groups"],
                extract_mentions(self.cleaned_data["individuals"]),
            )
            .active(community)
            .exclude(pk=sender.pk)
            .distinct()
        )
