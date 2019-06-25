from django import forms

from communikit.flags.models import Flag


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ("reason",)
        widgets = {"reason": forms.RadioSelect}
