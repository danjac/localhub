from django import forms

from localhub.photos.models import Photo


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
