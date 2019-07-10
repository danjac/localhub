from django import forms

from localite.communities.models import Membership


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ("role", "active")
        widgets = {"role": forms.RadioSelect}
