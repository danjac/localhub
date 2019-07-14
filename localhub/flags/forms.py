from django import forms

from localhub.flags.models import Flag


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ("reason",)
        widgets = {"reason": forms.RadioSelect}
