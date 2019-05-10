from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from communikit.communities.models import Community
from communikit.invites.models import Invite


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ("email",)

    def __init__(self, community: Community, *args, **kwargs):
        self.community = community
        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if self.community.members.filter(
            Q(emailaddress__email__iexact=email) | Q(email__iexact=email)
        ).exists():
            raise ValidationError(
                _(
                    "A user with this email address already belongs to "
                    "this community"
                )
            )
        if Invite.objects.filter(
            email__iexact=email, community=self.community
        ).exists():
            raise ValidationError(
                _("An invitation has already been sent to this email address")
            )
        return email
