from django import forms

from localhub.forms.widgets import ClearableImageInput, TypeaheadInput

from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:

        model = Photo
        fields = (
            "title",
            "image",
            "description",
            "allow_comments",
            "artist",
            "original_url",
            "cc_license",
        )
        widgets = {
            "title": TypeaheadInput,
            "image": ClearableImageInput,
        }
