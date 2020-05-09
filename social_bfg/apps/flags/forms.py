# Django
from django import forms

# Local
from .models import Flag


class FlagForm(forms.ModelForm):
    class Meta:
        model = Flag
        fields = ("reason",)
        widgets = {"reason": forms.RadioSelect}
