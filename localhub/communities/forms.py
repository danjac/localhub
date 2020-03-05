from django import forms

from localhub.forms.widgets import ClearableImageInput

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
        widgets = {"logo": ClearableImageInput}


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("role", "active")
        widgets = {"role": forms.RadioSelect}
