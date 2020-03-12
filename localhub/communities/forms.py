# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import forms
from django.utils.translation import gettext_lazy as _

from localhub.forms.widgets import ClearableImageInput, TypeaheadInput

from .models import Community, Membership


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = (
            "name",
            "logo",
            "tagline",
            "intro",
            "description",
            "terms",
            "google_tracking_id",
            "content_warning_tags",
            "public",
            "allow_join_requests",
            "blacklisted_email_domains",
            "blacklisted_email_addresses",
        )
        widgets = {"logo": ClearableImageInput, "content_warning_tags": TypeaheadInput}

        help_texts = {
            "logo": _("Logo will be rendered in PNG format."),
            "tagline": _("Summary shown in Communities page"),
            "intro": _("Text shown in Login and other pages to non-members."),
            "description": _(
                "Longer description of site shown to members in Description page."
            ),
            "terms": _(
                "Terms and conditions, code of conduct and other membership terms."
            ),
            "content_warning_tags": _(
                "Any posts containing these tags in their description "
                "will be automatically hidden by default."
            ),
            "email_domain": _(
                "Will add domain to notification emails from this site, e.g. "
                "notifications@this-domain.com. If left empty will use the site "
                "domain by default."
            ),
            "active": _("This community is currently live."),
            "public": _("Community is visible to non-members in Communities page."),
            "allow_join_requests": _(
                "Users can send requests to join this community. "
                "If disabled they will only be able to join if an admin sends "
                "them an invite."
            ),
            "blacklisted_email_addresses": _(
                "Join requests from these addresses will be automatically "
                "rejected. Separate with spaces."
            ),
        }


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("role", "active")
        widgets = {"role": forms.RadioSelect}
