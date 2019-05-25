from django import forms

from communikit.photos.models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:

        model = Photo
        fields = ("title", "tags", "image")
